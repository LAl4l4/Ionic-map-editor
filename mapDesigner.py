import json
import os

mapbase = [
    # 0 ---------------- 外围顶边全是 2 ----------------
    [2]*24,
    # 1
    [2] + [1]*22 + [2],
    # 2
    [2] + [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1] + [2],
    # 3
    [2] + [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1] + [2],
    # 4
    [2] + [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1] + [2],
    # 5
    [2] + [2]*22 + [2],
    # 6
    [2] + [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,1,1,1,1,1] + [2],
    # 7
    [2] + [1,1,1,1,1,1,1,1,1,1,2,2,1,1,1,1,1,1,2,2,1,1] + [2],
    # 8
    [2] + [1,1,1,1,1,2,2,1,1,1,1,1,2,2,1,1,1,1,1,1,1,1] + [2],
    # 9
    [2] + [1,2,2,1,1,1,1,1,2,2,1,1,1,1,1,2,2,1,1,1,2,1] + [2],
    # 10
    [2] + [1,1,1,1,2,2,1,1,1,1,1,2,2,1,1,1,1,2,2,1,1,1] + [2],
    # 11
    [2] + [1,1,2,2,1,1,1,2,2,1,1,1,1,2,2,1,1,1,2,2,1,1] + [2],
    # 12
    [2] + [1,1,1,1,1,1,2,1,1,1,2,2,1,1,1,1,1,2,1,1,1,1] + [2],
    # 13
    [2] + [1,2,2,1,1,1,1,1,1,2,2,1,1,1,1,1,2,2,1,1,1,1] + [2],
    # 14
    [2] + [1]*22 + [2],
    # 15 ---------------- 外围底边全是 2 ----------------
    [2]*24
]

TILE_INFO = {
    1: {
        "code": 1,
        "name": "back_stone", 
        "path": "", 
        "walkable": False, 
        "upThroughable": False
        },
    2: {
        "code": 2,
        "name": "stone", 
        "path": "Materials/map/Tiles/castleCenter.png", 
        "walkable": True,
        "upThroughable": False
        }
}

MAP_INFO = {
    "height": len(mapbase) * 100,
    "width": len(mapbase[0]) * 100,
    "tilesize": 100
}

Entity = [
    {
        "id":1,
        "position":[1000,300]
    }
]
    


playerSpawn = {
    "x": 200,
    "y": 200
}

enemy = [
    {"id": 2, "spawn": [200, 300], "delay": 0},
    {"id": 2, "spawn": [300, 300], "delay": 0},
    {"id": 1, "spawn": [800, 300], "delay": 0}#How many times it should spawn after game start
]
    
mapName = "start_cave"

gameMap = [[TILE_INFO[tile] for tile in row] for row in mapbase]

#下方为json打包

mapData = {
    "name": mapName,
    "playerSpawn": playerSpawn,
    "enemy": enemy,
    "tile_info": TILE_INFO,
    "map_info": MAP_INFO,
    "map": gameMap,
    "entity": Entity,
}

basepath = os.path.dirname(os.path.abspath(__file__))
filename = f"{mapName}.json"
filepath = os.path.join(basepath, filename)

with open(filepath, "w", encoding="utf-8") as f:
    json.dump(mapData, f, ensure_ascii=False, indent=2)