from common.enums import Platforms, EmailStatus
from platform_scripts.taichi import run_script as taichi_script
from platform_scripts.vblink import run_script as vblink_script
from platform_scripts.firekirin import run_script as firekirin_script
from platform_scripts.acebook import run_script as acebook_script
from platform_scripts.gamevault import run_script as gamevault_script
from platform_scripts.orionstar import run_script as orion_script
from platform_scripts.juwa import run_script as juwa_script
from platform_scripts.bluedragon import run_script as bluedragon_script
from platform_scripts.goldenDragon import run_script as goldendragon_script
from platform_scripts.milkyway import run_script as milkyway_script


def run_platform(subject_platform, each, username, amount):
    if subject_platform.lower() == "t" or subject_platform.lower() == "taichi":
        platform = Platforms.Taichi.value
    elif subject_platform.lower() == "f" or subject_platform.lower() == "kirin" or subject_platform.lower() == "firekirin":
        platform = Platforms.Firekirin.value
    elif subject_platform.lower() == "o" or subject_platform.lower() == "os" or "orion" in subject_platform.lower():
        platform = Platforms.Orionstar.value
    elif subject_platform.lower() == "v" or subject_platform.lower() == "vb" or subject_platform.lower() == "vblink" or "vblink" in subject_platform.lower():
        platform = Platforms.VBLink.value
    elif subject_platform.lower() == "g" or subject_platform.lower() == "gv" or subject_platform.lower() == "gamevault" or "gamevault" in subject_platform.lower():
        platform = Platforms.GameVault999.value
    elif subject_platform.lower() == "ab" or "ace" in subject_platform.lower() or "djwae" in subject_platform.lower():
        platform = Platforms.Acebook.value
    elif subject_platform.lower() == "j" or subject_platform.lower() == "juwa":
        platform = Platforms.Juwa.value
    elif subject_platform.lower() == "bd" or subject_platform.lower() == "bluedragon":
        platform = Platforms.BlueDragon.value
    elif subject_platform.lower() == "gd" or subject_platform.lower() == "goldendragon":
        platform = Platforms.GoldenDragon.value
    elif subject_platform.lower() == "mw" or subject_platform.lower() == "milkyway":
        platform = Platforms.Milkyway.value
    else:
        return False, "Platfrom Not Identified", ""
    user_platforms = each.platforms
    creds = None
    for each_user_platforms in user_platforms:
        if each_user_platforms.platform.name == platform:
            creds = (
                each_user_platforms.platform.username,
                each_user_platforms.platform.password,
                each_user_platforms.platform.url_key,
            )
    if amount and not creds:
        return False, "Creds not Set for Platform. ", platform
    elif not amount:
        return False, "Amount not Found.", platform
    else:
        if platform == Platforms.Taichi.value:
            res, msg = taichi_script(username, int(amount), creds[0], creds[1])
            return res, msg, platform
        if platform == Platforms.VBLink.value:
            res, msg = vblink_script(username, int(amount), creds[0], creds[1])
            return res, msg, platform
        if platform == Platforms.Firekirin.value:
            res, msg = firekirin_script(username, int(amount), creds[0], creds[1])
            return res, msg, platform
        if platform == Platforms.GameVault999.value:
            res, msg = gamevault_script(username, int(amount), creds[0], creds[1])
            return res, msg, platform
        if platform == Platforms.Acebook.value:
            res, msg = acebook_script(username, int(amount), creds[0], creds[1])
            return res, msg, platform
        if platform == Platforms.Orionstar.value:
            res, msg = orion_script(username, int(amount), creds[0], creds[1])
            return res, msg, platform
        if platform == Platforms.Juwa.value:
            res, msg = juwa_script(username, int(amount), creds[0], creds[1])
            return res, msg, platform
        if platform == Platforms.BlueDragon.value:
            res, msg = bluedragon_script(username, int(amount), creds[0], creds[1])
            return res, msg, platform
        if platform == Platforms.GoldenDragon.value:
            res, msg = goldendragon_script(username, int(amount), creds[0], creds[1],creds[2])
            return res, msg, platform
        if platform == Platforms.Milkyway.value:
            res, msg = milkyway_script(username, int(amount), creds[0], creds[1])
            return res, msg, platform
