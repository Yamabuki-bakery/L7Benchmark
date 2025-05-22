"""
    一個簡單腳本，用來讀取 clash gui 的 yaml 配置文件的節點信息，然後生成 v2ray 配置文件，
    Clash Verge - 訂閱 - 右鍵訂閱 - 打開文件
    該配置文件將會把每一個機場節點都對應到一個本地的 socks5 代理端口上，
    形成一個本地的 v2ray 代理池。
    目前只支持 ss 和 vmess (包括 ws) 兩種協議。

    使用方法：
      python v2ray-pool.py <config.yaml> <output_file>
    <output_file> 是輸出的配置文件名 (可選，默認輸出到 v2ray-pool.json)。
"""

import json, argparse, logging, yaml
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@dataclass
class SocksInbound:
    port: int
    listen: str = "127.0.0.1"
    protocol: str = "socks"
    settings: Dict[str, Any] = field(default_factory=lambda: {"auth": "noauth", "udp": True})
    tag: str = ""

@dataclass
class ShadowsocksServer:
    address: str
    port: int
    method: str
    password: str
    udp: bool = True

@dataclass
class WsSettings:
    path: str = "/"
    headers: Dict[str, str] = field(default_factory=lambda: {})

@dataclass
class StreamSettings:
    network: str = "tcp"
    security: str = "none"
    wsSettings: Optional[WsSettings] = None

@dataclass
class VmessServer:
    address: str
    port: int
    id: str
    alterId: int = 0
    security: str = "auto"
    network: str = "tcp"
    streamSettings: Optional[StreamSettings] = None

@dataclass
class OutboundConfig:
    protocol: str
    settings: Dict[str, Any]
    tag: str
    streamSettings: Optional[Dict[str, Any]] = None

@dataclass
class RoutingRule:
    inboundTag: List[str]
    outboundTag: str
    type: str = "field"

@dataclass
class V2RayConfig:
    log: Dict[str, str] = field(default_factory=lambda: {"loglevel": "warning"})
    inbounds: List[SocksInbound] = field(default_factory=lambda: [])
    outbounds: List[OutboundConfig] = field(default_factory=lambda: [])
    routing: Dict[str, List[RoutingRule]] = field(default_factory=lambda: {"rules": []})

    def to_json(self) -> str:
        """Convert the config to JSON string."""
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

def create_shadowsocks_outbound(server: dict[str, Any], tag: str) -> OutboundConfig:
    """Create a Shadowsocks outbound configuration from a server dict."""
    ss_server = ShadowsocksServer(
        address=server["server"],
        port=server["port"],
        method=server["cipher"],
        password=server["password"],
        udp=server.get("udp", True)
    )
    
    return OutboundConfig(
        protocol="shadowsocks",
        settings={"servers": [asdict(ss_server)]},
        tag=tag
    )

def create_vmess_outbound(server: dict[str, Any], tag: str) -> OutboundConfig:
    """Create a VMess outbound configuration from a server dict."""
    # Create stream settings if network is specified
    stream_settings = None
    network = server.get("network", "tcp")
    
    if network == "ws":
        ws_settings = WsSettings(
            path=server.get("ws-path", "/") or "/",
            headers=server.get("ws-headers", {}) or {}
        )
        stream_settings = StreamSettings(
            network=network,
            security=server.get("tls", "none"),
            wsSettings=ws_settings
        )
    
    vmess_server = VmessServer(
        address=server["server"],
        port=server["port"],
        id=server["uuid"],
        alterId=server.get("alterId", 0),
        security=server.get("cipher", "auto"),
        network=network,
        streamSettings=stream_settings
    )
    
    outbound_config = OutboundConfig(
        protocol="vmess",
        settings={"vnext": [{
            "address": vmess_server.address,
            "port": vmess_server.port,
            "users": [{
                "id": vmess_server.id,
                "alterId": vmess_server.alterId,
                "security": vmess_server.security
            }]
        }]},
        tag=tag
    )
    
    # Add stream settings if available
    if vmess_server.streamSettings:
        outbound_config.streamSettings = asdict(vmess_server.streamSettings)
    
    return outbound_config

def parse_clash_config(config_path: str) -> List[dict[str, Any]]:
    """Parse the Clash configuration file and extract proxy nodes."""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Extract proxies
    proxies = config.get('proxies', [])
    logging.info(f"Found {len(proxies)} proxy nodes in the configuration file.")
    
    return proxies

def generate_v2ray_config(proxies: List[dict[str, Any]], start_port: int = 10000) -> V2RayConfig:
    """Generate V2Ray configuration with an inbound port for each proxy."""
    config = V2RayConfig()
    
    for i, proxy in enumerate(proxies):
        # Skip nodes that appear to be information display entries
        if any(keyword in proxy.get("name", "") for keyword in ["流量", "官网", "剩余", "套餐", "导航"]):
            continue
        
        # Create an inbound port for this proxy
        port = start_port + i
        inbound_tag = f"socks-{proxy.get('name', str(i))}-{port}"
        inbound = SocksInbound(
            port=port,
            listen="127.0.0.1",  # Only listen on localhost for security
            protocol="socks",
            settings={"auth": "noauth", "udp": True},
            tag=inbound_tag
        )
        
        # Create an outbound for this proxy
        outbound_tag = f"proxy-{proxy.get('name', str(i))}-{port}"
        if proxy["type"] == "ss":
            outbound = create_shadowsocks_outbound({
                "server": proxy["server"],
                "port": proxy["port"],
                "cipher": proxy["cipher"],
                "password": proxy["password"],
                "udp": proxy.get("udp", True)
            }, outbound_tag)
        elif proxy["type"] == "vmess":
            outbound = create_vmess_outbound({
                "server": proxy["server"],
                "port": proxy["port"],
                "uuid": proxy["uuid"],
                "alterId": proxy.get("alterId", 0),
                "cipher": proxy.get("cipher", "auto"),
                "network": proxy.get("network", "tcp"),
                "ws-path": proxy.get("ws-path"),
                "ws-headers": proxy.get("ws-headers"),
                "tls": proxy.get("tls")
            }, outbound_tag)
        else:
            logging.warning(f"Unsupported proxy type: {proxy['type']} for {proxy['name']}, skipping")
            continue
        
        # Create a routing rule
        rule = RoutingRule(
            inboundTag=[inbound_tag],
            outboundTag=outbound_tag
        )
        
        # Add to the configuration
        config.inbounds.append(inbound)
        config.outbounds.append(outbound)
        config.routing["rules"].append(rule)
        
        logging.info(f"Added proxy {proxy['name']} on port {port}")
    
    return config

def main():
    parser = argparse.ArgumentParser(description="Generate V2Ray configuration from Clash config.")
    parser.add_argument("config", help="Path to the Clash configuration file")
    parser.add_argument("output", nargs='?', default="v2ray-pool.json", 
                        help="Output file name (default: v2ray-pool.json)")
    parser.add_argument("--start-port", type=int, default=10000,
                        help="Starting port number for SOCKS5 proxies (default: 10000)")
    args = parser.parse_args()
    
    # Parse the Clash config
    proxies = parse_clash_config(args.config)
    
    # Generate V2Ray config
    config = generate_v2ray_config(proxies, args.start_port)
    
    # Save the config
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(config.to_json())
    
    logging.info(f"V2Ray configuration saved to {args.output}")
    logging.info(f"Created {len(config.inbounds)} proxy entries, starting at port {args.start_port}")

if __name__ == "__main__":
    main()



