const { Router } = require('express');
const router = Router();

const fs = require('fs'); // modulo File System
const path = require('path');
const { PassThrough } = require('stream');
const uuid = require('uuid4');

router.get('/', (req, res) => {
   //res.render('index.ejs',{usuarios}); //Si no hay contenidos en usuarios, no aparece nada al principio

});
//Para recivir el torrent y guardarlo
router.post('/torrent', (req, res) => {
   let torrentContent = JSON.stringify(req.body);
   let { pieces, lastPiece, filepath, tracker, name, checksum, puertoTracker, id } = req.body
   console.log(req.body)
   fs.writeFileSync(`torrents/${name}.torrent`, torrentContent, 'utf-8'); //Agregar en alchivo usuarios.json el objeto
   res.json({ "Recibi": req.body })
})

//Para devolver una lista con los torrent de archivos que cuenta el servidor
router.get('/archivos', (req, res) => {
   var data = [];
   try {
      var ls = fs.readdirSync('torrents/');

      for (let index = 0; index < ls.length; index++) {
         const file = path.join('torrents/', ls[index]);
         var dataFile = null;
         try {
            dataFile = fs.lstatSync(file);
         } catch (e) { }

         if (dataFile) {
            data.push(
               {
                  path: file,
               });
         }
      }
   } catch (e) { }

   let lista = []
   console.log(data)
   data.forEach(element => {

      let torrent = fs.readFileSync(element.path)
      lista.push(JSON.parse(torrent)['name'])
   });

   console.log(lista)
   res.json(lista)
})

//Una vez seleccionado el archivo deseado, se llama a esta direccion para enviar el torrent deseado
router.get('/torrent', (req, res) => {
   let file_data_requested = req.query.name
   console.log("Holaa")
   console.log(file_data_requested)
   let file_name = file_data_requested + '.torrent'
   let torrent = fs.readFileSync(path.join('torrents/', file_name))
   console.log(torrent)
   res.json(JSON.parse(torrent))
})

module.exports = router;