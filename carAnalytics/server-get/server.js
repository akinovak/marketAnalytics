const express = require('express')
const morgan = require('morgan')
const bodyParser = require('body-parser')
const methodOverride = require('method-override')
const Mongo = require('mongodb')
const MongoClient = Mongo.MongoClient

const app = express()

const port = process.env.PORT || 5001

app.use(morgan('dev'))
app.use(bodyParser.json())

app.use(bodyParser.json({ limit: '100gb', extended: true }))
app.use(bodyParser.urlencoded({ limit: '100gb', extended: true }))
app.use(methodOverride())

let dbCar
MongoClient.connect("mongodb://localhost:27017/", { useNewUrlParser: true, useUnifiedTopology: true }, (err, db) => {
  if (err) throw err
  dbCar = db.db("testServerCarDb")
})

app.post('/getavgprice', (req, res) => {
    let make = req.body.make
    let model = req.body.model
    dbCar.collection('polovni').aggregate([
            {$match: {Marka: make, Model: model}}
        , {$group:
            {_id: null, avg_price: {$avg: "$cena"} }
            }
        ]).toArray(function(err, docs) {
        if (err) throw err
        res.send(docs)
    })
})

app.post('/getavgpricebykm', (req, res) => {
    let make = req.body.make
    let model = req.body.model
    let km = req.body.km
    dbCar.collection('polovni').aggregate([
            {$match: {Marka: make, Model: model, Kilometraza: {$lte:km+10000, $gte:km-10000}}}
        , {$group:
            {_id: null, avg_price: {$avg: "$cena"} }
            }
        ]).toArray(function(err, docs) {
        if (err) throw err
        res.send(docs)
    })
})


const server = app.listen(port, () => console.log(`Listening on port ${port}`))
