
pragma solidity >=0.5.0 <0.8.0;

contract Bank {
  int balance = 2;

  function funcion(int direccion) public returns (int a, int b) {
    int c = 2;
    if (c == 2) {
      c++;
    } else {
      c--;
    }

    if (c != 2) {
      if (c == 2) {

      }
    }

    while (c==2) {
      if (c<=2) {
        while(c==2) {}
      } else { c--;}
    }

    do {
      c++;
      continue;
    } while (c == 2);

    for (int i = 0; i<10; i++) {
      c++;
      break;
    }

    for (;;) {}
  }
}
