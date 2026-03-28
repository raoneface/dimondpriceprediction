from flask import Flask,request,render_template,jsonify
from src.pipelines.prediction_pipeline import CustomData,PredictPipeline
from src.logger import logging
import json
import os


application=Flask(__name__)

app=application

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
ARTIFACTS_DIR = os.path.join(PROJECT_ROOT, 'artifacts')


def load_model_accuracies():
    """Load model report generated during training for frontend display."""
    report_path = os.path.join(ARTIFACTS_DIR, 'model_report.json')
    if not os.path.exists(report_path):
        logging.warning("Model report not found at %s", report_path)
        return []

    with open(report_path, 'r') as report_file:
        report_data = json.load(report_file)

    # Sort by score descending so best model appears first.
    sorted_models = sorted(report_data.items(), key=lambda item: item[1], reverse=True)
    logging.debug("Loaded %d model scores from model report", len(sorted_models))
    return [
        {
            'name': model_name,
            'r2_score': round(float(score), 4),
            'accuracy_percent': round(float(score) * 100, 2)
        }
        for model_name, score in sorted_models
    ]

@app.route('/')
def home_page():
    logging.info("Home page requested")
    model_accuracies = load_model_accuracies()
    return render_template('index.html', model_accuracies=model_accuracies)


@app.route('/health', methods=['GET'])
def health_check():
    logging.info("Health check requested")
    model_path = os.path.join(ARTIFACTS_DIR, 'model.pkl')
    preprocessor_path = os.path.join(ARTIFACTS_DIR, 'preprocessor.pkl')
    model_report_path = os.path.join(ARTIFACTS_DIR, 'model_report.json')

    artifacts_status = {
        'model': os.path.exists(model_path),
        'preprocessor': os.path.exists(preprocessor_path),
        'model_report': os.path.exists(model_report_path)
    }

    model_accuracies = load_model_accuracies()
    logging.info(
        "Health status | artifacts_ready=%s | model=%s | preprocessor=%s | report=%s | models_in_report=%d",
        all(artifacts_status.values()),
        artifacts_status['model'],
        artifacts_status['preprocessor'],
        artifacts_status['model_report'],
        len(model_accuracies),
    )

    return jsonify({
        'status': 'ok',
        'service': 'diamond-price-prediction',
        'artifacts_ready': all(artifacts_status.values()),
        'artifacts': artifacts_status,
        'models_in_report': len(model_accuracies)
    }), 200

@app.route('/predict',methods=['GET','POST'])

def predict_datapoint():
    logging.info("Predict endpoint requested | method=%s", request.method)
    model_accuracies = load_model_accuracies()

    if request.method=='GET':
        return render_template('form.html', model_accuracies=model_accuracies)
    
    else:
        try:
            data=CustomData(
                carat=float(request.form.get('carat')),
                depth = float(request.form.get('depth')),
                table = float(request.form.get('table')),
                x = float(request.form.get('x')),
                y = float(request.form.get('y')),
                z = float(request.form.get('z')),
                cut = request.form.get('cut'),
                color= request.form.get('color'),
                clarity = request.form.get('clarity')
            )
            logging.debug(
                "Prediction input received | carat=%s depth=%s table=%s x=%s y=%s z=%s cut=%s color=%s clarity=%s",
                request.form.get('carat'),
                request.form.get('depth'),
                request.form.get('table'),
                request.form.get('x'),
                request.form.get('y'),
                request.form.get('z'),
                request.form.get('cut'),
                request.form.get('color'),
                request.form.get('clarity'),
            )

            final_new_data=data.get_data_as_dataframe()
            predict_pipeline=PredictPipeline()
            pred=predict_pipeline.predict(final_new_data)

            results=round(pred[0],2)
            logging.info("Prediction completed successfully | predicted_price=%s", results)

            return render_template('form.html', final_result=results, model_accuracies=model_accuracies)
        except Exception:
            logging.exception("Prediction request failed")
            raise
    

if __name__=="__main__":
    app.run(host='0.0.0.0',debug=True)