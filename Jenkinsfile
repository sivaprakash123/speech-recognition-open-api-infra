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
                                defaultValue: false,
                                name: 'ENABLE_INGRESS'
                            ), 
                            booleanParam(
                                defaultValue: false, 
                                name: 'ENABLE_ENVOY_ADMIN'
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
                                defaultValue: '3.2.34',
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
                    sh "python3 deploy.py --namespace $params.NAMESPACE --api-updated $params.API_UPDATED --enable-ingress $params.ENABLE_INGRESS --image-name $params.IMAGE_NAME --image-version $params.IMAGE_VERSION --enable-envoy-admin $params.ENABLE_ENVOY_ADMIN"
            }
        }
    }
}
