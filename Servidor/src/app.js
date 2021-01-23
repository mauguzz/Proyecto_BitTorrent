const express = require ('express');
const app = express();
const path = require ('path');  //Para acceder a las carpetas de mi proyecto a partir del context path
const morgan = require ('morgan');  //Middleware para la gestion de peticiones

//settings
app.set('port', 4000);  //Puerto donde se ejecuta la apliacaion
app.set('view engine', 'ejs'); //El motor de mis plantillas sera ejs

//middleware
app.use(morgan('dev'));
app.use(express.urlencoded({extended:false})); // traducción de formularios en JSON

//routes
app.use(require('./routes/index'));

app.use((req, resp, next)=>{
    resp.status(404).send("recurso no encontrado en la ubicación especificada ...");
}); 

module.exports = app;