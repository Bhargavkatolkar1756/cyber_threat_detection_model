from flask import Flask, request, render_template
import pickle
import numpy as np
import traceback

app = Flask(__name__)

# Load the model
model_path = 'best_xgboost_model.pkl'
try:
    with open(model_path, 'rb') as file:
        model = pickle.load(file)
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Debug: Check if the model is loaded
        if model is None:
            print("Model not loaded.")
            return render_template('index.html', prediction_text="Error: Model not loaded.")

        # Input Parsing
        destination_port = request.form.get('destinationPort')
        flow_duration = request.form.get('flowDuration')
        total_fwd_packets = request.form.get('totalFwdPackets')
        total_backward_packets = request.form.get('totalBackwardPackets')

        # Debug: Print received inputs
        print(f"Inputs received: Destination Port: {destination_port}, Flow Duration: {flow_duration}, "
              f"Total Forward Packets: {total_fwd_packets}, Total Backward Packets: {total_backward_packets}")

        # Input Validation
        if not all([destination_port, flow_duration, total_fwd_packets, total_backward_packets]):
            return render_template('index.html', prediction_text="Error: All input fields are required.")

        # Convert inputs to integers and validate data
        try:
            features = np.array([[int(destination_port),
                                  int(flow_duration),
                                  int(total_fwd_packets),
                                  int(total_backward_packets)]])
        except ValueError as ve:
            print(f"ValueError: {ve}")
            return render_template('index.html', prediction_text="Error: Inputs must be numeric.")

        # Debug: Print prepared feature array and shape
        print(f"Feature array: {features}")
        print(f"Feature array shape: {features.shape}")

        # Make Prediction
        prediction = model.predict(features)
        print(f"Prediction Raw Output: {prediction}")

        # Convert Prediction to Human-Readable Result
        output = 'Threat Detected' if prediction[0] == 1 else 'No Threat Detected'
        print(f"Prediction Result: {output}")

        return render_template('index.html', prediction_text=f'Prediction: {output}')

    except Exception as e:
        # Debug: Log detailed traceback for easier troubleshooting
        print(f"Error occurred: {traceback.format_exc()}")
        return render_template('index.html', prediction_text=f"Error: {str(e)}")

if __name__ == "__main__":
    app.run(debug=True)
