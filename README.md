Kubernetes Pod Reader Using Service Account
This guide walks you through setting up a Kubernetes deployment that uses a service account to list all pods in a cluster, using a Python script. It also includes steps to install the necessary Python dependencies (kubernetes library) inside the container.

Prerequisites
Kubernetes cluster up and running
kubectl installed and configured to interact with the cluster
Steps
1. Create the Service Account
Create a service account with the name pod-reader-sa in the default namespace.

# service-account.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: pod-reader-sa
  namespace: default
Apply this file:

kubectl apply -f service-account.yaml
2. Create RBAC Permissions
Grant the service account permission to list and get pods by creating a ClusterRole and binding it to the service account.

# rbac.yaml
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
Apply this file:

kubectl apply -f rbac.yaml
3. Create the Deployment
Create a deployment that uses the service account pod-reader-sa. This deployment will install the kubernetes Python client using pip, then run a Python script to list all pods in the cluster.

# python-pod.yaml
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
Apply this file:

kubectl apply -f python-pod.yaml
4. Verify
Check the logs of the deployment to ensure that the pods are being listed:

kubectl logs deployment/pod-reader-deployment
You should see the output listing all pods in the cluster:

Namespace: default, Pod Name: pod-reader-deployment-xxxxxx
Namespace: kube-system, Pod Name: coredns-xxxxxx
...
Conclusion
This setup allows the Python script to list all pods in the Kubernetes cluster using the created service account. The kubernetes Python client is installed within the container, and the necessary RBAC permissions ensure that the service account can access pod information.