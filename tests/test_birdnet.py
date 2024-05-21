"""Tests for the birdnet module."""

import datetime
from pathlib import Path
from uuid import UUID

import rich

from phone_sensors.birdnet import SensorStatus, analyze_audio

SPECIES_LIST = """
Accipiter cooperii_Cooper's Hawk
Agelaius phoeniceus_Red-winged Blackbird
Anas platyrhynchos_Mallard
Anas rubripes_American Black Duck
Ardea herodias_Great Blue Heron
Baeolophus bicolor_Tufted Titmouse
Branta canadensis_Canada Goose
Bucephala albeola_Bufflehead
Bucephala clangula_Common Goldeneye
Buteo jamaicensis_Red-tailed Hawk
Cardinalis cardinalis_Northern Cardinal
Certhia americana_Brown Creeper
Colaptes auratus_Northern Flicker
Columba livia_Rock Pigeon
Corvus brachyrhynchos_American Crow
Corvus corax_Common Raven
Cyanocitta cristata_Blue Jay
Cygnus olor_Mute Swan
Dryobates pubescens_Downy Woodpecker
Dryobates villosus_Hairy Woodpecker
Dryocopus pileatus_Pileated Woodpecker
Eremophila alpestris_Horned Lark
Haemorhous mexicanus_House Finch
Haemorhous purpureus_Purple Finch
Haliaeetus leucocephalus_Bald Eagle
Junco hyemalis_Dark-eyed Junco
Larus argentatus_Herring Gull
Larus delawarensis_Ring-billed Gull
Lophodytes cucullatus_Hooded Merganser
Melanerpes carolinus_Red-bellied Woodpecker
Meleagris gallopavo_Wild Turkey
Melospiza melodia_Song Sparrow
Mergus merganser_Common Merganser
Mergus serrator_Red-breasted Merganser
Passer domesticus_House Sparrow
Poecile atricapillus_Black-capped Chickadee
Regulus satrapa_Golden-crowned Kinglet
Sialia sialis_Eastern Bluebird
Sitta canadensis_Red-breasted Nuthatch
Sitta carolinensis_White-breasted Nuthatch
Spinus pinus_Pine Siskin
Spinus tristis_American Goldfinch
Spizelloides arborea_American Tree Sparrow
Sturnus vulgaris_European Starling
Thryothorus ludovicianus_Carolina Wren
Turdus migratorius_American Robin
Zenaida macroura_Mourning Dove
Zonotrichia albicollis_White-throated Sparrow
""".splitlines()


def test_analyze_audio():
    """Test analyze_audio function."""
    file_path = Path("./example.wav")
    sensor_status = SensorStatus(
        sensor_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        timestamp=datetime.datetime.now(datetime.timezone.utc),
        lat=52.52,
        lon=13.405,
        accuracy=10.0,
        battery=0.5,
        temperature=20.0,
    ).add_coordinates()
    result = analyze_audio(file_path, sensor_status, 0.25, remove_file=False)
    rich.print(result)
    assert len(result) > 0
