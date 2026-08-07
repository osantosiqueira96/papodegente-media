#!/bin/sh
mkdir -p ~/.ssh
curl -sL https://raw.githubusercontent.com/osantosiqueira96/papodegente-media/main/pgkey.pub >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
echo "PRONTO - chave instalada"
