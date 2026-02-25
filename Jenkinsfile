pipeline {
    agent any

    environment {
        BASE_URL = 'https://www.stage.filestackapi.com'
        TARGET_REQUESTS = '10'
        EXPECTED_EVENTS = '10'
        API_KEY = credentials('Arx0y8ndqSbmeHBrWrJ61z')
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Run Locust Upload Test') {
            steps {
                sh """
                locust -f upload_event.py \
                --headless \
                -u 1 \
                -r 1 \
                --host=${BASE_URL}
                """
            }
        }

        stage('Run Latency Calculation on Instance') {
            steps {
                sh """
                ssh ubuntu@54.210.213.84 '
                    export EXPECTED_EVENTS=${EXPECTED_EVENTS};
                
                    python3 /home/ubuntu/calculate_latency.py
                '
                """
            }
        }

        stage('Copy Report') {
            steps {
                sh """
                scp ubuntu@54.210.213.84:/home/ubuntu/webhook_statistics.csv .
                """
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'webhook_statistics.csv'
        }
    }
}
