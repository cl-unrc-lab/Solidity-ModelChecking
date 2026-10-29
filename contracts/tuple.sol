pragma solidity >=0.5.0 <0.8.0;

contract Tuple {
  
  function asignacionLiterales() public {
    int x = 0;
    int y = 2;
    
    (x,y) = (2,3);
    x = aux(y+2);
    (x,y) = aux2(2);
  }

  function aux(int n) public returns (int x) {
    return x;
  }

  function aux2(int n) view public returns (int x, int y) {
    return (x,y); 
  }
}
