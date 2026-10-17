pipeline {
    agent any

    environment {
        HEADLESS = '1'
    }

    options {
        timestamps()
    }

    stages {
        stage('Setup') {
            steps {
                bat 'python -m venv venv'
                bat 'venv\\Scripts\\python -m pip install -r requirements.txt'
            }
        }
        stage('Smoke tests') {
            steps {
                bat 'venv\\Scripts\\python -m pytest -m smoke -v'
            }
        }
        stage('Full regression') {
            steps {
                bat 'venv\\Scripts\\python -m pytest -v --junitxml=reports\\junit.xml'
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: 'reports/junit.xml'
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
        }
    }
}