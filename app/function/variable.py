from datetime import date

Version: str = "v3.3.0LTS"
VersionType: str = "release"
versionDate: date = date(2026, 3, 1)

UpdateAvailable: bool = False
UpdateInfo: str = None

REGIONVALIDATIONKEY: str = "StaticHttpRegionInfo, Assembly-CSharp"

DownloadSources = [
    {
        "name": "清风 API",
        "base_url": "https://api.qingfengawa.top/FengAmongUsTool-Asset/"
    },
    {
        "name": "GhProxy (CloudFlare)",
        "base_url": "https://gh-proxy.org/https://github.com/QingFengTechnology/FengAmongUsTool-Asset/raw/refs/heads/main/"
    },
    {
        "name": "GhProxy (HongKong)",
        "base_url": "https://hk.gh-proxy.org/https://github.com/QingFengTechnology/FengAmongUsTool-Asset/raw/refs/heads/main/"
    },
    {
        "name": "Github",
        "base_url": "https://raw.githubusercontent.com/QingFengTechnology/FengAmongUsTool-Asset/refs/heads/main/"
    }
]

ToolTitle: str = """
███████╗███████╗███╗   ██╗ ██████╗     ████████╗ ██████╗  ██████╗ ██╗     
██╔════╝██╔════╝████╗  ██║██╔════╝     ╚══██╔══╝██╔═══██╗██╔═══██╗██║     
█████╗  █████╗  ██╔██╗ ██║██║  ███╗       ██║   ██║   ██║██║   ██║██║     
██╔══╝  ██╔══╝  ██║╚██╗██║██║   ██║       ██║   ██║   ██║██║   ██║██║     
██║     ███████╗██║ ╚████║╚██████╔╝       ██║   ╚██████╔╝╚██████╔╝███████╗
╚═╝     ╚══════╝╚═╝  ╚═══╝ ╚═════╝        ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝
"""