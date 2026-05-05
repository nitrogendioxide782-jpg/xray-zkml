import onnxruntime as ort
import numpy as np


class XRayModel:

    def __init__(self, model_path="ezkl.onnx"):

        self.session = ort.InferenceSession(model_path)
        self.input_name = self.session.get_inputs()[0].name


    def predict(self, image_tensor):

        outputs = self.session.run(
            None,
            {self.input_name: image_tensor}
        )

        logits = outputs[0]

        prob = self._sigmoid(logits)
        prob = np.array(prob).reshape(-1)[0]

        return {
            "logits": logits,
            "probability": float(prob)
        }


    def _sigmoid(self, x):
        return 1 / (1 + np.exp(-x))