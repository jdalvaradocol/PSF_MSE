/*=============================================================================
 * Author: Jose David <alvaradomoreno.jd@gmail.com>
 * Date: 2022/07/25
 *===========================================================================*/

/*=====[Inclusions of function dependencies]=================================*/

#include "TP1_A.h"
#include "sapi.h"
#include "arm_math.h"

uint16_t printQ7(q7_t n,char *buf)
{
   return sprintf(buf,"q7: Hexa:0x%x Decimal:%i \r\n",n,n);
}

q7_t multiQ7(q7_t a,q7_t b)
{
   q15_t ans;
   ans=a*b;
   ans<<=1;
   return (q7_t) (ans>>8);
}

int main ( void ) {
   uint16_t sample = 0;
   int16_t len;
   char buf [ 200 ];

   boardConfig (                  );
   uartConfig  ( UART_USB, 460800 );
   adcConfig   ( ADC_ENABLE       );
   cyclesCounterInit ( EDU_CIAA_NXP_CLOCK_SPEED );

   q7_t a	  = 0x40;
   q7_t b 	  = 0x23;
   q7_t resul = 0x00;

   while(1) {
      cyclesCounterReset();

      resul = multiQ7( a, b);
      len   = printQ7( resul,buf);
      uartWriteByteArray ( UART_USB ,buf ,len);

      sample++;
      gpioToggle ( LED1 );                                           // este led blinkea a fs/2

      while(cyclesCounterRead()< EDU_CIAA_NXP_CLOCK_SPEED/1)
         ;
   }
}
