from ipaddress import ip_address, ip_network

from fastapi import HTTPException, Request


async def is_yookassa_ip(req: Request):
    YOOKASS_IP_ADDRESSES = [
        "185.71.76.0/27",
        "185.71.77.0/27",
        "77.75.153.0/25",
        "77.75.156.11",
        "77.75.156.35",
        "77.75.154.128/25",
        "2a02:5180::/32",
    ]

    client_ip = (
        req.headers.get("x-forwarded-for", req.client.host).split(",")[0].strip()
    )

    if not any(
        ip_address(client_ip) in ip_network(net) for net in YOOKASS_IP_ADDRESSES
    ):
        raise HTTPException(403)
