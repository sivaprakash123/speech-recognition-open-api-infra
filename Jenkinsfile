pipeline {
    agent any

    stages {
        stage('Setup parameters') {
            steps{
                script {
                    properties([
                        parameters([
                            booleanParam(
                                defaultValue: true, 
                                name: 'API_UPDATED'
                            ),
                            booleanParam(
                                defaultValue: true, 
                                name: 'ENABLE_INGRESS'
                            ),
                            string(
                                defaultValue: 'nltm', 
                                name: 'NAMESPACE'
                            ),
                            string(
                                defaultValue: 'gcr.io/ekstepspeechrecognition/speech_recognition_model_api', 
                                name: 'IMAGE_NAME'
                            ),
                            string(
                                defaultValue: '2.1.2', 
                                name: 'IMAGE_VERSION'
                            )
                        ])
                    ])
                }
            }
        }
        stage("Deploy") {
            steps {
                    sh "kubectl get pods -n nltm"
                    sh "python3 deploy.py --namespace $params.NAMESPACE --api-updated $params.API_UPDATED --enable-ingress $params.ENABLE_INGRESS --image-name $params.IMAGE_NAME --image-version $params.IMAGE_VERSION"
            }
        }
    }
}
