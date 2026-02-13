pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'my-python-app'
        DOCKER_TAG = "${BUILD_NUMBER}"
        DOCKER_HUB_CREDS = credentials('dockerhub-creds')
        // Using 'best-accuracy' credential for comparison, but it's a secret text, so we map it to a variable
        BEST_ACCURACY_CRED = credentials('best-accuracy') 
        PYTHON_ENV = 'venv'
        // Default threshold if secret is not set or empty, though credentials binding usually handles this
        BASELINE_ACCURACY = '0.5' 
    }

    stages {
        stage('Checkout') {
            steps {
                // Stage 1: Checkout
                checkout scm
            }
        }

        stage('Setup Python Virtual Environment') {
            steps {
                // Stage 2: Setup Python Virtual Environment
                sh '''
                    python3 -m venv ${PYTHON_ENV}
                    . ${PYTHON_ENV}/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Train Model') {
            steps {
                // Stage 3: Train Model
                sh '''
                    . ${PYTHON_ENV}/bin/activate
                    python src/train.py
                '''
            }
        }

        stage('Read Accuracy') {
            steps {
                // Stage 4: Read Accuracy
                script {
                    def metrics = readJSON file: 'app/artifacts/metrics.json'
                    env.CURRENT_ACCURACY = metrics.accuracy
                    echo "Current Accuracy: ${env.CURRENT_ACCURACY}"
                }
            }
        }

        stage('Compare Accuracy') {
            steps {
                // Stage 5: Compare Accuracy
                script {
                    // Assuming BEST_ACCURACY_CRED contains a float value
                    // If strictly following specific instructions for "best-accuracy" credential:
                    // "Compare current accuracy with value stored in: best-accuracy"
                    
                    def bestAcc = env.BEST_ACCURACY_CRED?.trim() ?: env.BASELINE_ACCURACY
                    echo "Best Accuracy (Baseline): ${bestAcc}"
                    
                    // Simple string comparison or float comparison in Groovy
                    // Using shell for reliable float comparison if needed, or groovy float parsing
                    def current = env.CURRENT_ACCURACY.toFloat()
                    def best = bestAcc.toFloat()
                    
                    if (current > best) {
                        env.MODEL_IMPROVED = 'true'
                        echo "New model is better! (${current} > ${best})"
                    } else {
                        env.MODEL_IMPROVED = 'false'
                        echo "New model is not better. (${current} <= ${best})"
                    }
                }
            }
        }

        stage('Build Docker Image (Conditional)') {
            when {
                environment name: 'MODEL_IMPROVED', value: 'true'
            }
            steps {
                // Stage 6: Build Docker Image
                // "Build Docker image only if the new model outperforms the stored baseline"
                // Authenticate using: dockerhub-creds is implicitly handled if pushing, 
                // but usually login is needed for push. Steps say "authenticate" here.
                
                sh 'echo "Building Docker Image..."'
                // Build from root context using the deployment/Dockerfile
                sh "docker build -f deployment/Dockerfile -t ${DOCKER_IMAGE}:${DOCKER_TAG} -t ${DOCKER_IMAGE}:latest ."
            }
        }

        stage('Push Docker Image (Conditional)') {
            when {
                environment name: 'MODEL_IMPROVED', value: 'true'
            }
            steps {
                // Stage 7: Push Docker Image
                sh 'echo "Pushing Docker Image..."'
                // Login to Docker Hub using credentials
                sh 'echo $DOCKER_HUB_CREDS_PSW | docker login -u $DOCKER_HUB_CREDS_USR --password-stdin'
                
                sh "docker push ${DOCKER_IMAGE}:${DOCKER_TAG}"
                sh "docker push ${DOCKER_IMAGE}:latest"
            }
        }
    }

    post {
        always {
            // Task 5: Artifact Archiving
            // "Regardless of build success or failure, Jenkins must archive: app/artifacts/**"
            archiveArtifacts artifacts: 'app/artifacts/**', fingerprint: true
            
            // Clean up workspace to save space (optional but good practice)
            // cleanWs() 
        }
    }
}
