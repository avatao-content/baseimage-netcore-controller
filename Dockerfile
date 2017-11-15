FROM avatao/controller:ubuntu-16.04
ENV DOTNET_CLI_TELEMETRY_OPTOUT=1

USER root

RUN apt-get update \
	&& apt-get install -qy \
		apt-transport-https \
	&& curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/microsoft.gpg \
	&& sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/microsoft-ubuntu-xenial-prod xenial main" > /etc/apt/sources.list.d/dotnetdev.list' \
	&& apt-get update \
	&& apt-get install -qy dotnet-sdk-2.0.2 \
	&& adduser --disabled-password --gecos ',,,' --uid 2000 controller


