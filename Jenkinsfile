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

        stage('Verify Generated Reports') {

            steps {

                bat '''
                echo.
                echo ==================================================
                echo GENERATED REPORTS
                echo ==================================================
                dir output /s
                '''

            }

        }

        stage('Archive Reports') {

            steps {

                archiveArtifacts(
                    artifacts: 'output/**/*',
                    fingerprint: true,
                    allowEmptyArchive: false
                )

            }

        }

        stage('Publish HTML Report') {

            steps {

                publishHTML(target: [

                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,

                    reportDir: 'output/latest',
                    reportFiles: 'Executive_Report.html',
                    reportName: 'AWS Daily Health Report'

                ])

            }

        }

    }

    post {

        success {

            echo ''
            echo '=================================================='
            echo 'AWS Health Check Completed Successfully'
            echo '=================================================='

        }

        failure {

            echo ''
            echo '=================================================='
            echo 'AWS Health Check Failed'
            echo '=================================================='

        }

        always {

            cleanWs()

        }

    }

}