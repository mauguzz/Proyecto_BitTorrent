const app = require('./app');

/* Definición de función asincrona */
async function main(){  
  await app.listen(app.get("port"));  // instrucción asincrona
  console.log("server on port", app.get("port"));
}

main();

/*
  express usa
  rutas
    .get
    .post

  ejs (motor de plantillas) me permite meter codigo JS en HTML
    <p>
    <% console.log('ejemplo') %>
    </p>

  Contexto de la aplicaicon
  URL
   localhost: 3000/EjemploFormulario

  morgan (Middleware. Para gestionar los datos de la peticion en express)

  uuid (Modulo que genera un identificador unico y en este caso se utilizazra par identificar cada
            objeto en el JSON)
*/