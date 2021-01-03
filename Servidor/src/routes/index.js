const {Router} = require('express');
const router = Router();

const fs = require('fs'); // modulo File System
const uuid = require('uuid4');

 
//const usuariosJSONr = fs.readFileSync('torrents/archivo.torrent','utf-8'); //Para leer usuarios.json, regresa una cadena
//const usuarios = JSON.parse(usuariosJSONr); //La cadena se convierte en un archivo JSON

//Especificación de la ruta inicial de la app
//Cuando en tu navegador le des localhost:4000 se ejecuta lo siguiente
router.get('/',(req, res)=>{
  //res.render('index.ejs',{usuarios}); //Si no hay contenidos en usuarios, no aparece nada al principio
  
});

router.post('/torrent', (req, res)=>{
    let torrentContent=JSON.stringify(req.body);
    console.log(req.body)
    fs.writeFileSync(`torrents/torrent_${uuid()}.torrent`, torrentContent,'utf-8'); //Agregar en alchivo usuarios.json el objeto
    res.json({"Recibi": req.body})
    /*    let torrent_info = {
        piecelen:info.piecelen,
        checksum:info.checksum
    }

    let torrent = {
        announce:announce, 
        info:torrent_info
      };
      */
    //recibe un json
    //guarda el json en un archivo torrent
})

//Localhost:4000/new-data
router.get('/requestFile',(req, res)=>{
    let id=req.params('id')
  res.render('new-data')
});


router.post('/new-data',(req, res) =>{
  const {nombre, carrera, semestre} = req.body; //los datos que te ingresen en el formulario en formato
                                                    //JSON (express.urlencoding)
  let usuario = {
    id:uuid(), 
    nombre:nombre,
    carrera:carrera, 
    semestre:semestre
  };

  usuarios.push(usuario);

  // convierte a string el arreglo de objetos javascript
  const usuariosJSON = JSON.stringify(usuarios);

  fs.writeFileSync('src/usuarios.json', usuariosJSON,'utf-8'); //Agregar en alchivo usuarios.json el objeto
                              //que se encuentra en JSON

  res.redirect('/'); //Redirecciona a la ruta principal
});

router.get('/delete/:id',(req,res)=>{
   
});

module.exports = router;