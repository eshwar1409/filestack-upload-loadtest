pipeline {
    agent any

    // -----------------------------
    // Environment Variables
    // -----------------------------
    environment {
        BASE_URL = 'https://www.stage.filestackapi.com'   // Your API host
        TARGET_REQUESTS = '10'                             // Number of requests for testing
        EXPECTED_EVENTS = '10'                             // Expected number of webhook events
        API_KEY = credentials('filestack-api-key')        // Jenkins Secret Text credential
    }

    stages {

        // -----------------------------
        // Checkout from GitHub
        // -----------------------------
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        // -----------------------------
        // Install Python Dependencies
        // -----------------------------
        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
                sh 'pip install locust pandas numpy'
            }
        }

        // -----------------------------
        // Run Locust Upload Test
        // -----------------------------
        stage('Run Locust Upload Test') {
            steps {
                sh """
                locust -f upload_event.py \
                --headless \
                -u ${TARGET_REQUESTS} \
                -r 1 \
                --host=${BASE_URL}
                """
            }
        }

        // -----------------------------
        // Run Latency Calculation on Remote Instance
        // -----------------------------
        stage('Run Latency Calculation on Instance') {
            steps {
                sshagent(['']) {  // Jenkins SSH private key credential
                    sh """
                    ssh ubuntu@54.210.213.84 '
                        export EXPECTED_EVENTS=${EXPECTED_EVENTS};
                        python3 /home/your-username/calculate_latency.py
                    '
                    """
                }
            }
        }

        // -----------------------------
        // Copy Latency Report Locally
        // -----------------------------
        stage('Copy Report') {
            steps {
                sshagent(['instance-ssh-key']) {
                    sh """
                    scp ubuntu@54.210.213.84:/home/your-username/webhook_statistics.csv .
                    scp ubuntu@54.210.213.84:/home/your-username/webhook1_detailed.csv .
                    """
                }
            }
        }
    }

    // -----------------------------
    // Archive Reports
    // -----------------------------
    post {
        always {
            archiveArtifacts artifacts: 'webhook_statistics.csv, webhook1_detailed.csv'
        }
    }
}
