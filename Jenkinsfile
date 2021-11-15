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
                                defaultValue: 'test',
                                name: 'NAMESPACE'
                            ),
                            string(
                                defaultValue: 'gcr.io/ekstepspeechrecognition/speech_recognition_model_api', 
                                name: 'IMAGE_NAME'
                            ),
                            string(
                                defaultValue: '2.1.6',
                                name: 'IMAGE_VERSION'
                            )
                        ])
                    ])
                }
            }
        }
        stage("Deploy") {
            steps {
                sh "chmod +x ./scripts/install_helm.sh"
                sh "./scripts/install_helm.sh"
                withCredentials([
                    file(credentialsId: 'meity-eks-kube', variable: 'KUBECONFIG'),
                    string(credentialsId: 'meity-eks-iam-access', variable: 'AWS_ACCESS_KEY_ID'),
	                string(credentialsId: 'meity-eks-iam-secret', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh 'python3 -m pip install pyyaml'
                    sh "python3 deploy.py --namespace $params.NAMESPACE --api-updated $params.API_UPDATED --enable-ingress $params.ENABLE_INGRESS --image-name $params.IMAGE_NAME --image-version $params.IMAGE_VERSION"
                }
            }
        }
    }
}
