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
            agent any
            steps {
                // Stage 1: Checkout
                checkout scm
            }
        }

        stage('Model Training & Evaluation') {
            agent {
                docker { 
                    image 'python:3.10' 
                    // Mount the workspace so artifacts persist
                    reuseNode true 
                }
            }
            steps {
                // Stage 2: Setup Python Virtual Environment
                // Note: Inside python container, we might not need venv, but following lab steps.
                // However, the container is ephemeral for this stage.
                
                sh 'pip install -r requirements.txt'
                
                // Stage 3: Train Model
                sh 'python src/train.py'
                
                // Stage 4: Read Accuracy
                script {
                    def metrics = readJSON file: 'app/artifacts/metrics.json'
                    env.CURRENT_ACCURACY = metrics.accuracy
                    echo "Current Accuracy: ${env.CURRENT_ACCURACY}"
                }
                
                // Stage 5: Compare Accuracy
                script {
                    def bestAcc = env.BEST_ACCURACY_CRED?.trim() ?: env.BASELINE_ACCURACY
                    echo "Best Accuracy (Baseline): ${bestAcc}"
                    
                    def current = env.CURRENT_ACCURACY.toFloat()
                    def best = bestAcc.toFloat()
                    
                    if (current > best) {
                        env.MODEL_IMPROVED = 'true'
                        echo "New model is better! (${current} > ${best})"
                    } else {
                        env.MODEL_IMPROVED = 'false'
                        echo "New model is not better. (${current} <= ${best})"
                    }
                    
                    // Allow MODEL_IMPROVED to be visible in subsequent stages if possible.
                    // Environment variables set within a stage/agent are usually local.
                    // We might need to write to a file to persist the decision to the next stage 
                    // or assume 'agent any' shares the same workspace variables if defined globally.
                    // Actually, 'env.VAR' updates are propagated if not shadowed.
                }
            }
        }

        stage('Docker Build & Push') {
            agent any
            when {
                expression { return env.MODEL_IMPROVED == 'true' }
            }
            steps {
                // Stage 6: Build Docker Image
                sh 'echo "Building Docker Image..."'
                sh "docker build -f deployment/Dockerfile -t ${DOCKER_IMAGE}:${DOCKER_TAG} -t ${DOCKER_IMAGE}:latest ."
                
                // Stage 7: Push Docker Image
                sh 'echo "Pushing Docker Image..."'
                sh 'echo $DOCKER_HUB_CREDS_PSW | docker login -u $DOCKER_HUB_CREDS_USR --password-stdin'
                sh "docker push ${DOCKER_IMAGE}:${DOCKER_TAG}"
                sh "docker push ${DOCKER_IMAGE}:latest"
            }
        }
    }

    post {
        always {
            // Ensure we are in a node context for archiving
            script {
                // Task 5: Artifact Archiving
                // "Regardless of build success or failure, Jenkins must archive: app/artifacts/**"
                if (fileExists('app/artifacts')) {
                    archiveArtifacts artifacts: 'app/artifacts/**', fingerprint: true
                }
            }
            
            // Clean up workspace to save space (optional but good practice)
            // cleanWs() 
        }
    }
}
