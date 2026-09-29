"""
5x5 Mini-Male (Mini-Chess)
Põhiprogramm / Main entry point.

Käivitamine:
    python main.py
"""
import sys
from gui import MiniChessGUI


def main():
    print("=" * 50)
    print("5x5 MINI-MALE (Mini-Chess) käivitatud!")
    print("Laud: 5x5 (A-E, 1-5)")
    print("Arvuti vastane: Minimax algoritm koos Alpha-Beta kärpimisega")
    print("Juhtimine:")
    print("  - Hiireklõps või lohistamine käigu tegemiseks")
    print("  - Uus mäng / Võta tagasi / Raskusaste küljepaneelilt")
    print("  - Kiirklahvid: 'U' (võta tagasi), 'N' (uus mäng), 'F' (pööra laud)")
    print("=" * 50)

    app = MiniChessGUI()
    app.run()


if __name__ == "__main__":
    main()
