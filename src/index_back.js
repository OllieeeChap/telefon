
// on importe les dépendances
const five = require("johnny-five");
const Raspi = require("raspi-io").RaspiIO;
var fs = require("fs");
var lame = require("lame");
var Speaker = require("node-speaker");

// Création instance audio
var speaker = new Speaker();
var decoder = new lame.Decoder();

// on déclare la board
const board = new five.Board({ io: new Raspi() });

// Une fois la carte prête
board.on("ready", function() {

  // configuration du button de raccrochage du combiné
  var hangupButton = new five.Button({
    pin: "GPIO21",
    isPullup: true,
    holdtime: 10
  });

  // déclenchement lorsque l'on décroche
  hangupButton.on("up", function() {
    board.info("Phone", "PICK UP");
  });

  // déclenchement lorsque l'on raccroche
  hangupButton.on("down", function() {
    board.info("Phone", "HANG UP");
  });
});
var Rotary = require("./Rotary");

// creation d'une instance de notre classe
const rotary = new Rotary();

// declaration d'un bouton qui recevra les impulsions
var rotaryButton = new five.Button({
  pin: "GPIO17",
  isPullup: true,
  holdtime: 10,
  invert: true
});

// lorsqu'on detecte une impulsion, on envoie l'info à notre instance de Rotary
rotaryButton.on("up", () => rotary.onPulse());

// lorsque le rotary nous indique que la composition est terminée (timeout > 2000ms)
rotary.on("compositionend", number => {
  board.info("Rotary", `COMPOSE ${number}`);
  // on récupère le "number" entier
  // -> déclenchement du son en fonction du number
})

