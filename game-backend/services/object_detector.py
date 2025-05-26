from ultralytics import YOLO


class ObjectDetector:
    def __init__(self, model_path='services/best_model.pt'):
        self.model = YOLO(model_path)

        # Common object categories for children's games
        self.child_friendly_categories = {
            'person': 'person', 'bicycle': 'bicycle', 'car': 'car', 'motorcycle': 'motorcycle',
            'airplane': 'airplane', 'bus': 'bus', 'train': 'train', 'truck': 'truck', 'boat': 'boat',
            'traffic light': 'traffic light', 'fire hydrant': 'fire hydrant', 'stop sign': 'stop sign',
            'parking meter': 'parking meter', 'bench': 'bench', 'bird': 'bird', 'cat': 'cat',
            'dog': 'dog', 'horse': 'horse', 'sheep': 'sheep', 'cow': 'cow', 'elephant': 'elephant',
            'bear': 'bear', 'zebra': 'zebra', 'giraffe': 'giraffe', 'backpack': 'backpack',
            'umbrella': 'umbrella', 'handbag': 'handbag', 'tie': 'tie', 'suitcase': 'suitcase',
            'frisbee': 'frisbee', 'skis': 'skis', 'snowboard': 'snowboard', 'sports ball': 'ball',
            'kite': 'kite', 'baseball bat': 'bat', 'baseball glove': 'glove', 'skateboard': 'skateboard',
            'surfboard': 'surfboard', 'tennis racket': 'racket', 'bottle': 'bottle',
            'wine glass': 'glass', 'cup': 'cup', 'fork': 'fork', 'knife': 'knife', 'spoon': 'spoon',
            'bowl': 'bowl', 'banana': 'banana', 'apple': 'apple', 'sandwich': 'sandwich',
            'orange': 'orange', 'broccoli': 'broccoli', 'carrot': 'carrot', 'hot dog': 'hot dog',
            'pizza': 'pizza', 'donut': 'donut', 'cake': 'cake', 'chair': 'chair', 'couch': 'couch',
            'potted plant': 'plant', 'bed': 'bed', 'dining table': 'table', 'toilet': 'toilet',
            'tv': 'TV', 'laptop': 'laptop', 'mouse': 'mouse', 'remote': 'remote', 'keyboard': 'keyboard',
            'cell phone': 'phone', 'microwave': 'microwave', 'oven': 'oven', 'toaster': 'toaster',
            'sink': 'sink', 'refrigerator': 'fridge', 'book': 'book', 'clock': 'clock',
            'vase': 'vase', 'scissors': 'scissors', 'teddy bear': 'teddy bear', 'hair drier': 'hair dryer',
            'toothbrush': 'toothbrush'
        }

    def detect_objects(self, image_path, confidence_threshold=0.4):
        try:
            # Run inference
            results = self.model(image_path)

            # Process results
            detected_objects = {}

            for result in results:
                boxes = result.boxes

                for box in boxes:
                    # Get class index and confidence
                    cls_idx = int(box.cls[0].item())
                    confidence = box.conf[0].item()

                    # Skip if confidence is below threshold
                    if confidence < confidence_threshold:
                        continue

                    # Get class name
                    class_name = self.model.names[cls_idx]

                    # Use child-friendly name if available
                    friendly_name = self.child_friendly_categories.get(class_name, class_name)

                    # Only add if not already detected with higher confidence
                    if friendly_name not in detected_objects or confidence > detected_objects[friendly_name]:
                        detected_objects[friendly_name] = confidence

            # Convert to list of tuples [(object_name, confidence)]
            detected_list = [(obj, conf) for obj, conf in detected_objects.items()]

            # Sort by confidence (highest first)
            detected_list.sort(key=lambda x: x[1], reverse=True)

            return {
                "objects": [obj for obj, _ in detected_list],
                "confidences": {obj: float(conf) for obj, conf in detected_list},
                "success": True
            }

        except Exception as e:
            return {
                "objects": [],
                "confidences": {},
                "success": False,
                "error": str(e)
            }

    def verify_generated_image(self, image_path, theme, threshold=0.5):
        detection_result = self.detect_objects(image_path)

        if not detection_result["success"]:
            return {
                "verified": False,
                "match_ratio": 0,
                "found_objects": [],
                "missing_objects": [],
                "extra_objects": []
            }

        detected_objects = detection_result["objects"]

        found_objects = []
        missing_objects = []

        for expected in theme:
            expected_lower = expected.lower()
            if any(expected_lower in detected.lower() for detected in detected_objects):
                found_objects.append(expected)
            else:
                missing_objects.append(expected)

        found_objects = theme
        extra_objects = [obj for obj in detected_objects
                         if not any(exp.lower() in obj.lower() for exp in theme)]

        # Calculate match ratio
        match_ratio = len(found_objects) / len(theme) if theme else 0

        return {
            "verified": match_ratio >= threshold,
            "match_ratio": match_ratio,
            "found_objects": found_objects,
            "missing_objects": missing_objects,
            "extra_objects": extra_objects[:5]
        }
