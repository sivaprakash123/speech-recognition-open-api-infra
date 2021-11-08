## speech-recognition-open-api-infra

This project uses helm to deploy Open Speech API and its complete infrastructure to kubernetes.
### Prerequisites:
1. Go to infra root folder by running the following: `cd infra`
2. You can either install ingress controller or nginx pod to expose these services to public.
- To use ingress controller:
    Install the following:
    ```
        helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
        helm repo update

        helm install ingress-nginx ingress-nginx/ingress-nginx -n <namespace-name>
    ```
    or 
    ```
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.0.0/deploy/static/provider/cloud/deploy.yaml
    ```
- To use nginx pod:
    Run the following command:
    ```
    kubectl apply -f nginx/nginx.yaml -n <namespace-name>
    ```
3. To create secret for tls, do the following:
```
kubectl create secret tls asr-model-v2-secret \     
  --cert=vakyansh-secret/vakyansh.crt \
  --key=vakyansh-secret/vakyansh.key -n test
```
### Next steps:
- Go to infra root folder by running the following if not already inside infra folder: `cd infra`
- To deploy models, do the following:
    1. Do changes if needed in asr-model-v2
    2. Run the following to install: `helm install <release-name> asr-model-v2/ --set namespace=<namespace> --set env.languages='["<language>"]' -n <namespace>`

    To Upgrade:
    1. Do changes and package it(Follow steps 1 and 2 in above steps).
    2. Run the following to install: `helm upgrade <release-name> asr-model-v2/ --set namespace=<namespace> --set env.languages='["<language>"]' -n <namespace>`

- To deploy envoy infra with ingress, do the following:
    1. Do changes if needed in asr-model-v2
    2. Run the following to install: `helm install <release-name> envoy/ -n <namespace> `

    To Upgrade:
    1. Do changes and package it(Follow steps 1 and 2 in above steps).
    2. Run the following to install: `helm upgrade <release-name> envoy/ -n <namespace>`

### Reference:
1. For the installation command to deploy 

### To View all resources:
1. kubectl get all --namespace <namespace-name>
2. `helm list -n <namespace-name>` - to check releases.
3. kubectl get pods --namespace <namespace-name>
