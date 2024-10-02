To get a list of Kubernetes pods using a service account in Python, you can use the kubernetes Python client library. 
This script assumes that you have configured a service account with the necessary RBAC (Role-Based Access Control) permissions to list pods.
1. Create a Service Account
First, create a service account in your Kubernetes cluster. You can define the service account using a YAML file and apply it with kubectl:

yaml
Copy code
# service-account.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: pod-reader-sa  # Name of the service account
  namespace: default   # Namespace where the service account will be created
To create the service account, apply this file using kubectl:

bash
Copy code
kubectl apply -f service-account.yaml
This creates a service account named pod-reader-sa in the default namespace.

2. Create ClusterRole and ClusterRoleBinding
Next, create a ClusterRole to allow the service account to list pods and a ClusterRoleBinding to bind this role to the service account.

yaml
Copy code
# rbac.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: pod-reader-role  # Name of the ClusterRole
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: pod-reader-rolebinding  # Name of the ClusterRoleBinding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: pod-reader-role  # Bind to the ClusterRole defined above
subjects:
- kind: ServiceAccount
  name: pod-reader-sa  # Bind to the service account created earlier
  namespace: default   # Namespace of the service account
Apply this file using kubectl:

bash
Copy code
kubectl apply -f rbac.yaml
This configuration grants the pod-reader-sa service account the ability to list and watch pods in the entire cluster.

3. Deploy Python Script Using the Service Account
To use this service account in a Kubernetes pod that will run the Python script, you need to create a pod or deployment that uses the service account.

Here’s an example of a deployment that uses the service account:

apiVersion: apps/v1
kind: Deployment
metadata:
  name: pod-reader-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: pod-reader
  template:
    metadata:
      labels:
        app: pod-reader
    spec:
      serviceAccountName: pod-reader-sa  # Use the created service account
      containers:
      - name: pod-reader
        image: python:3.9-slim  # Use the python image
        command: ["/bin/sh", "-c"]  # Use shell to run multiple commands
        args:
        - |
          pip install kubernetes &&
          python -c "
          from kubernetes import client, config
          config.load_incluster_config()
          v1 = client.CoreV1Api()
          pods = v1.list_pod_for_all_namespaces(watch=False)
          for pod in pods.items:
              print(f'Namespace: {pod.metadata.namespace}, Pod Name: {pod.metadata.name}')"

To apply this, save it to a file and apply it with kubectl:

bash
Copy code
kubectl apply -f python-pod.yaml
4. Python Script (Running inside Kubernetes)
Here’s a more explicit version of the Python script that can be used when running in Kubernetes using the service account:

python
Copy code
from kubernetes import client, config

def list_pods():
    # Load the in-cluster configuration
    config.load_incluster_config()

    # Initialize the CoreV1Api
    v1 = client.CoreV1Api()

    # List all pods in all namespaces
    pods = v1.list_pod_for_all_namespaces(watch=False)
    
    for pod in pods.items:
        print(f"Namespace: {pod.metadata.namespace}, Pod Name: {pod.metadata.name}")

if __name__ == '__main__':
    list_pods()
5. Testing and Verification
After you deploy the pod running the script:

Use kubectl to check the logs and verify that the script is listing pods as expected.
bash
Copy code
kubectl logs deployment/pod-reader-deployment
The logs should show a list of all the pods in the cluster.
Full YAML Files for Reference
service-account.yaml
yaml
Copy code
apiVersion: v1
kind: ServiceAccount
metadata:
  name: pod-reader-sa
  namespace: default
rbac.yaml
yaml
Copy code
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: pod-reader-role
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: pod-reader-rolebinding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: pod-reader-role
subjects:
- kind: ServiceAccount
  name: pod-reader-sa
  namespace: default
python-pod.yaml
yaml
Copy code
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pod-reader-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: pod-reader
  template:
    metadata:
      labels:
        app: pod-reader
    spec:
      serviceAccountName: pod-reader-sa
      containers:
      - name: pod-reader
        image: python:3.9-slim
        command: ["python", "-u", "-c", "
        from kubernetes import client, config
        config.load_incluster_config()
        v1 = client.CoreV1Api()
        pods = v1.list_pod_for_all_namespaces(watch=False)
        for pod in pods.items:
            print(f'Namespace: {pod.metadata.namespace}, Pod Name: {pod.metadata.name}')"
        ]
This setup will allow the Python script to list all pods in the Kubernetes cluster using the service account.
