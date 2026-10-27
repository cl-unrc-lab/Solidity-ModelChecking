pragma solidity >=0.5.0 <0.8.0;

contract Bank {
  int balance = 2;

  function funcion(int direccion) public returns (int a, int b) {
    int c = 2;
    c = 2 + 2;
    c = 2 - 2;
    c = 2 * 2;
    c = 2 % 2;
    c = 2 / 2;
    c = 2 & 2;
    c = 2 | 2;
    c = 2 ^ 2;
    c = 2 ** 2;
    c = 2 << 2;
    c = 2 >> 2;
    
    // booleano
    bool b = true;
    b = true && true;
    b = true || true;
    b = 2 == 2;
    b = 2 < 2;
    b = 2 <= 2;
    b = 2 > 2;
    b = 2 >= 2;
    b = 2 != 2;

    // asignaciones 
    c &= 2;
    c /= 2;
    c = 2;
    c <<= 2;
    c -= 2;
    c %= 2;
    c |= 2;
    c += 2;
    c >>= 2;
    c *= 2;
    c ^= 2;

    //Unarios 
    b = !b;
    c++;
    c--;
    ++c;
    --c;
  }
}
