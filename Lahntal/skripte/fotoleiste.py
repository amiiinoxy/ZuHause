"""Gleich große Fotoausschnitte im QGIS-Layout; Original-JPEGs bleiben erhalten."""
from pathlib import Path
from qgis.core import (QgsCoordinateReferenceSystem, QgsLayoutItemMap,
                       QgsLayoutPoint, QgsLayoutSize, QgsRasterLayer, QgsRectangle)
from qgis.PyQt.QtGui import QImageReader


def add_photo_panel(layout, project, base, group, number, x, y,
                    width=54.7, height=30):
    base = Path(base)
    original = base / 'fotos' / f'{number:02d}.jpg'
    reader = QImageReader(str(original))
    size = reader.size()
    raw_w, raw_h = size.width(), size.height()
    transformation = int(reader.transformation())
    assert raw_w > 0 and raw_h > 0 and transformation in (0, 4)
    rotation = 90 if transformation == 4 else 0

    # Technische Pixelkoordinaten ausschließlich für den Foto-Layoutausschnitt.
    # Der VRT verweist relativ auf das JPEG und verändert keine Bildpixel.
    vrt = base / 'symbole' / f'bildausschnitt_{number:02d}.vrt'
    bands = ''.join(
        f'<VRTRasterBand dataType="Byte" band="{band}">'
        f'<ColorInterp>{color}</ColorInterp><SimpleSource>'
        f'<SourceFilename relativeToVRT="1">../fotos/{number:02d}.jpg</SourceFilename>'
        f'<SourceBand>{band}</SourceBand>'
        f'<SrcRect xOff="0" yOff="0" xSize="{raw_w}" ySize="{raw_h}"/>'
        f'<DstRect xOff="0" yOff="0" xSize="{raw_w}" ySize="{raw_h}"/>'
        '</SimpleSource></VRTRasterBand>'
        for band, color in enumerate(('Red', 'Green', 'Blue'), 1))
    vrt.write_text(
        f'<VRTDataset rasterXSize="{raw_w}" rasterYSize="{raw_h}">'
        '<SRS>EPSG:3857</SRS><GeoTransform>0,1,0,0,0,-1</GeoTransform>'
        + bands + '</VRTDataset>', encoding='utf-8')
    raster = QgsRasterLayer(str(vrt), f'Foto {number:02d} – nur Bildkoordinaten')
    assert raster.isValid()
    raster.setCustomProperty('nur_layoutfoto', True)
    project.addMapLayer(raster, False)
    group.addLayer(raster).setItemVisibilityChecked(False)

    picture = QgsLayoutItemMap(layout)
    picture.setId(f'Foto_{number:02d}')
    layout.addLayoutItem(picture)
    picture.attemptMove(QgsLayoutPoint(x, y))
    picture.attemptResize(QgsLayoutSize(width, height))
    picture.setCrs(QgsCoordinateReferenceSystem('EPSG:3857'))
    picture.setLayers([raster])
    picture.setKeepLayerSet(True)
    picture.setBackgroundEnabled(False)

    oriented_w, oriented_h = ((raw_h, raw_w) if rotation else (raw_w, raw_h))
    factor = max(width / oriented_w, height / oriented_h)
    view_w, view_h = width / factor, height / factor
    center_x, center_y = raw_w / 2, -raw_h / 2
    if number == 6 and rotation == 90:
        # Oberer Ausschnitt des Hochformats: Die Turmkrone bleibt sichtbar.
        center_x = view_h / 2
    picture.zoomToExtent(QgsRectangle(center_x - view_w / 2, center_y - view_h / 2,
                                      center_x + view_w / 2, center_y + view_h / 2))
    picture.setMapRotation(rotation)
    return picture
