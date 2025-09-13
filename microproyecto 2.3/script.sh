#!/usr/bin/env bash
set -e
export DEBIAN_FRONTEND=noninteractive

# --- Paquetes base ---
sudo apt-get update -y
sudo apt-get install -y curl apt-transport-https ca-certificates gnupg lsb-release \
  conntrack socat ebtables ethtool unzip git

# --- Docker (driver para Minikube) ---
sudo apt-get install -y docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker vagrant

# --- kubectl (cliente k8s) ---
sudo curl -fsSLo /usr/local/bin/kubectl \
  https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
sudo chmod +x /usr/local/bin/kubectl

# --- Minikube (clúster local) ---
curl -fsSLo /tmp/minikube.deb https://storage.googleapis.com/minikube/releases/latest/minikube_latest_amd64.deb
sudo dpkg -i /tmp/minikube.deb || { sudo apt-get -f install -y && sudo dpkg -i /tmp/minikube.deb; }
rm -f /tmp/minikube.deb

# --- Helm (opcional, para monitoreo tipo kube-prometheus-stack) ---
curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# --- Workspace mapeado ---
mkdir -p /home/vagrant/work
sudo chown -R vagrant:vagrant /home/vagrant/work
ln -sfn /vagrant/miniproyecto2 /home/vagrant/work/miniproyecto2

# --- Iniciar Minikube 2 nodos y habilitar addons ---
su - vagrant -c "minikube start --nodes=2 --driver=docker --cpus=2 --memory=3072"
su - vagrant -c "minikube addons enable metrics-server"
su - vagrant -c "minikube addons enable dashboard"
su - vagrant -c "kubectl get nodes -o wide || true"

echo 'Provision listo. Si Docker recién se agregó al grupo, vuelve a entrar: exit && vagrant ssh servidorUbuntu'
