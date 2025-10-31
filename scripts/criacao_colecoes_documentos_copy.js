use web_scraping_sites_rss;

db.createCollection('sites');

db.sites.createIndex({url_rss: 1},{unique:true});

db.createCollection('sites', {
    validator: {
        $jsonSchema :{
            bsonType: "object",
            properties: {
                id_site: { bsonType: "int" },
                nome :{
                    bsonType: "string",
                    minLength: 0,
                    maxLength: 50,
                    
                },
                url: { 
                  bsonType: "string", 
                  pattern: "^(https?:\\/\\/)?([\\w\\-]+\\.)+[\\w\\-]+(\\/[\\w\\-\\._~:\\/?#\\[\\]@!$&'()*+,;=]*)?$",
                  minLength: 5,
                  maxLength: 200
                },
                data_criacao: {
                    bsonType: "date"
                }
            }
        }
    }, validationLevel: "strict"   
    }
);

db.sites.insertMany(
    [
        {
            id_site: 1,
            nome : "G1 Ribeirão Preto",
            url_rss: "https://g1.globo.com/rss/g1/sp/ribeirao-preto-franca",
            data_criacao: new Date()
        },
        {
            id_site: 2,
            nome : "G1 Pará",
            url_rss: "https://g1.globo.com/rss/g1/pa/para/",
            data_criacao: new Date()
        },
        {
            id_site: 3,
            nome : "Tecnologia e Games",
            url_rss: "https://g1.globo.com/dynamo/tecnologia/rss2.xml",
            data_criacao: new Date()
        }
    ]
)

db.sites.find().pretty();





db.createCollection("noticias", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["id_site", "noticias"],
      properties: {
        id_site: {
          bsonType: "int",
          description: "ID do site é obrigatório"
        },
        noticias: {
          bsonType: "array",
          minItems: 1,
          items: {
            bsonType: "object",
            required: ["id_noticia", "titulo", "autor", "data_hora", "texto"],
            properties: {
              id_noticia: { bsonType: "string" },
              titulo: { bsonType: "string" },
              autor: { bsonType: "string" },
              data_hora: { bsonType: "date" },
              texto: { bsonType: "string" }
            }
          }
        }
      }
    }
  }
});


db.noticias.find({ id_site: 3 })
db.noticias.deleteMany({})