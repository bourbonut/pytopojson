from pytopojson.transform import transform

class Object(object):
    def __init__(self):
        self.transform_point = None
        self.arcs = None

    def __call__(self, topology, o):
        self.transform_point = transform(topology.get("transform", None))
        self.arcs = topology["arcs"]
        return self.geometry(o)

    def arc(self, i, points):
        if any(points):
            points.pop()

        arcs = self.arcs[~i if i < 0 else i]
        for k, arc in enumerate(arcs):
            points.append(self.transform_point(arc, k))

        if i < 0:
            j = len(points) - len(arcs)
            points = points[:j] + points[:j - 1:-1]

    def point(self, p):
        return self.transform_point(p)

    def line(self, arcs):
        points = list()
        for arc in arcs:
            self.arc(arc, points)

        # This should never happen per the specification.
        if len(points) < 2:
            points.append(points[0])

        return points

    def ring(self, arcs):
        points = self.line(arcs)
        # This may happen if an arc has only two points.
        if len(points) < 4:
            points += [points[0]] * (4 - len(points))
        return points

    def polygon(self, arcs):
        return list(map(self.ring, arcs))

    def geometry(self, o):
        _type = o.get("type", None)

        if _type == "GeometryCollection":
            return {
                "type": _type,
                "geometries": list(map(self.geometry, o["geometries"])),
            }
        elif _type == "Point":
            coordinates = self.point(o["coordinates"])
        elif _type == "MultiPoint":
            coordinates = list(map(self.point, o["coordinates"]))
        elif _type == "LineString":
            coordinates = self.line(o["arcs"])
        elif _type == "MultiLineString":
            coordinates = list(map(self.line, o["arcs"]))
        elif _type == "Polygon":
            coordinates = self.polygon(o["arcs"])
        elif _type == "MultiPolygon":
            coordinates = list(map(self.polygon, o["arcs"]))
        else:
            return None

        return {"type": _type, "coordinates": coordinates}


class Feature(object):
    def __init__(self):
        self.object = Object()

    def __call__(self, topology, o, *args, **kwargs):
        if isinstance(o, str):
            o = topology["objects"][o]

        if o.get("type") == "GeometryCollection":
            features = [self.feature(topology, geometry) for geometry in o["geometries"]]
            return {"type": "FeatureCollection", "features": features}
        else:
            return self.feature(topology, o)

    def feature(self, topology, o):
        feature = {
            "type": "Feature",
            "properties": o.get("properties", {}),
            "geometry": self.object(topology, o),
        }

        id = o.get("id")
        bbox = o.get("bbox")
        # Add missing elements if they are not None
        if id is not None and bbox is not None:
            feature.update({"id": id, "bbox": bbox})
        elif id is not None:
            feature.update({"id": id})

        return feature
