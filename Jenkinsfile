pipeline {

    agent any

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(
            numToKeepStr: '30',
            artifactNumToKeepStr: '30'
        ))
    }

    parameters {

        choice(
            name: 'CLIENT',
            choices: [
                'ATB',
                'BOQ',
                'BHFS',
                'COOP',
                'EQUIFAX',
                'FLEETCOR',
                'GENERALI',
                'IAG',
                'LFS',
                'MGL',
                'MIZUHO',
                'NBS',
                'SUNCORP',
                'TABCORP'
            ],
            description: 'Select AWS Customer'
        )

    }

    environment {
        AWS_DEFAULT_REGION = 'us-east-1'
        PYTHONUNBUFFERED = '1'
    }

    stages {

        stage('Checkout Source') {
            steps {
                checkout scm

                script {
                    currentBuild.displayName = "#${BUILD_NUMBER} ${params.CLIENT}"
                }
            }
        }

        stage('Install Python Dependencies') {

            steps {

                bat '''
                python -m pip install --upgrade pip
                pip install -r requirements.txt
                '''

            }
        }

        stage('Verify AWS Credentials') {

            steps {

                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding',
                    credentialsId: 'aws-master-account']
                ]) {

                    bat '''
                    @echo off

                    aws sts get-caller-identity >nul 2>&1

                    if %ERRORLEVEL%==0 (

                        echo.
                        echo ==================================================
                        echo AWS Credentials Verified Successfully
                        echo ==================================================

                    ) else (

                        echo.
                        echo ==================================================
                        echo ERROR : AWS Credentials Verification Failed
                        echo ==================================================

                        exit /b 1
                    )
                    '''
                }
            }
        }

        stage('Run AWS Health Check') {

            steps {

                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding',
                    credentialsId: 'aws-master-account']
                ]) {

                    bat '''
                    @echo off

                    echo.
                    echo ==================================================
                    echo AWS DAILY HEALTH CHECK FRAMEWORK
                    echo ==================================================
                    echo Client      : %CLIENT%
                    echo Build No    : %BUILD_NUMBER%
                    echo Workspace   : %WORKSPACE%
                    echo ==================================================

                    python -u main.py

                    if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%
                    '''

                }
            }
        }

        stage('Archive Reports') {

            steps {

                archiveArtifacts artifacts: 'output/**/*', allowEmptyArchive: true

            }
        }

    }

    post {

        success {

            echo ''
            echo '==============================================='
            echo 'AWS Health Check Completed Successfully'
            echo '==============================================='

            /*
            emailext(
                subject: "AWS Daily Health Report - ${params.CLIENT}",
                body: "Health Check completed successfully.",
                attachmentsPattern: "output/**/*",
                to: "yourteam@symphonyai.com"
            )
            */

            /*
            Teams Notification will be added later
            */

        }

        failure {

            echo ''
            echo '==============================================='
            echo 'AWS Health Check Failed'
            echo '==============================================='

        }

        always {

            cleanWs()

        }
    }
}
