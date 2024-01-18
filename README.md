> ## NOTA: Sobre el código de mi proyecto terminal de ingeniería telemática:
> 
> El código de dicho proyecto se encuentra en un repositorio de mi otra cuenta de GitHub: github.com/mauguzmor. Sin embargo, es un repositorio protegido.
> 
> Si está interesado en conocer una muestra de dicho código, contácteme al correo mauricio.guzz@outlook.com.
> 
> Recomiendo visitar mi portafolio de proyectos para conocer de qué trata mi proyecto terminal de ingeniería telemática:
> qué temas de investigación abarcó, el software de simulación de eventos discretos que diseñé y desarrollé, que arquitecturas implementé,
> y como utilicé conocimiento tanto de la academia como de la industria para resolver distintos problemas que se me presentaron durante el desarrollo
> de este proyecto. Haga clic en el enlace siguiente:
> 
> [Simulador de eventos discretos para la evaluación de protocolos de comunicaciones para enlaces ópticos satelitales](https://mauguzz.notion.site/Proyecto-de-titulaci-n-Caracterizaci-n-y-dise-o-de-estrategia-de-control-de-flujo-para-un-enlace-p-209b460cd8f349989ae0d2578e4301fc)

# Proyecto_BitTorrent
Proyecto de la materia de Sistemas Distribuidos de la carrera de Ingeniería Telemática en UPIITA del Instituto Politécnico Nacional.

En este proyecto se trabajó con el lenguaje de programación Python para desarrollar un sistema de transferencia de archivos P2P con un protocolo similar a BitTorrent.

El servidor de directorio de archivos se desarrolló en NodeJS. A este servidor se conectan los Clientes (desarrollados en Python) para consultar cuáles archivos hay disponibles. Los mismos clientes publican los archivos que comparten en ese directorio. Cuando un cliente quiere descargar un archivo, consulta el directorio en el servidor de NodeJS y lo descarga, donde aparece la dirección de los peers de donde puede descargar el archivo. Entonces el cliente, teniendo la dirección de los peers, inicia conexiones con ellos para descargar el archivo por fragmentos. Una vez que se completa la descarga, el cliente publica en el servidor NodeJS que también posee el archivo, por lo que si otro cliente quiere descargar el mismo archivo, ya hay más peers en el enjambre que tienen el archivo.

Como ya se mencionó, se utilizaron tecnologías como Python y NodeJS. Por otro lado, para las conexiones entre clientes, se utilizó GRPC, un framework para llamadas a procedimientos remotos desarrollado por Google. El objetivo de la materia fue precisamente diseñar sistemas distribuidos y uno de los temas fueron RPC.
