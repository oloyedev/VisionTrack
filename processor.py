
def create_analytics():
    return {
        "seen_objects": {},
        "total_by_class": {},
        "visible_by_class": {}
    }


def update_analytics(detections, analytics):
    visible_by_class = {}

    for item in detections:
        object_name = item["object"]
        track_id = item["track_id"]

        
        visible_by_class[object_name] = (
            visible_by_class.get(object_name, 0) + 1
        )

        
        if track_id is not None and track_id not in analytics["seen_objects"]:
            analytics["seen_objects"][track_id] = object_name

            analytics["total_by_class"][object_name] = (
                analytics["total_by_class"].get(object_name, 0) + 1
            )

    analytics["visible_by_class"] = visible_by_class

    return analytics
