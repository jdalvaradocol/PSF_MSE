/*=============================================================================
 * Author: Jose David <alvaradomoreno.jd@gmail.com>
 * Date: 2022/07/25
 *===========================================================================*/

/*=====[Inclusions of function dependencies]=================================*/

#include "TP1_B.h"
#include "sapi.h"
#include "arm_math.h"
#include "arm_const_structs.h"

#define BITS 10						// cantidad de bits usado para cuantizar
uint32_t tick	= 0   ;
uint16_t tone	= 440 ;


struct header_struct {
   char		pre[4];
   uint32_t id;
   uint16_t N;
   uint16_t fs ;
   q15_t 	maxADC;
   q15_t 	minADC;
   q15_t 	rmsADC;
   q15_t 	maxDAC;
   q15_t 	minDAC;
   q15_t 	rmsDAC;
   char		pos[4];
} __attribute__ ((packed));

struct header_struct header={"head",0,1024,50000,0,0,0,0,0,0,"tail"};

void trigger(int16_t threshold)
{
   while((adcRead(CH1)-512)>threshold)
	  ;
   while((adcRead(CH1)-512)<threshold)
	  ;
   return;
}

int main ( void )

{

	uint16_t sample = 0;
	uint32_t Index = 0;
	int16_t adc [ header.N	   ];
	int16_t dac [ header.N	   ];

	boardConfig		 (							);
	uartConfig		 ( UART_USB ,460800			);
	adcConfig		 ( ADC_ENABLE				);
	dacConfig		 ( DAC_ENABLE				);
	cyclesCounterInit ( EDU_CIAA_NXP_CLOCK_SPEED );

	while(1)
	{

		cyclesCounterReset();

		uartWriteByteArray ( UART_USB ,(uint8_t* )&dac[sample] ,sizeof(dac[0]) );	 // envia el sample ANTERIOR
		uartWriteByteArray ( UART_USB ,(uint8_t* )&adc[sample] ,sizeof(adc[0]) );	 // envia el sample ANTERIOR

		adc[sample]	= (((int16_t )adcRead(CH1)-512)>>(10-BITS))<<(6+10-BITS);			 // PISA el sample que se acaba de mandar con una nueva muestra

		float t = (tick)/((float)header.fs);
		tick++;

		int16_t dac_signal = 512 * arm_sin_f32 (t*tone*2*PI)+512;

		dac[sample] = dac_signal;

		dacWrite( DAC, dac_signal);		 // tono

		if ( ++sample==header.N )
		{
			 gpioToggle ( LEDR );						  // este led blinkea a fs/N

			sample = 0;

			arm_max_q15 ( (q15_t)(adc) ,header.N/2+1 ,&header.maxADC , &Index );
			arm_min_q15 ( (q15_t)(adc) ,header.N/2+1 ,&header.minADC , &Index );
			arm_rms_q15 ( (q15_t)(adc) ,header.N/2+1 ,&header.rmsADC );

			arm_max_q15 ( (q15_t)(dac) ,header.N/2+1 ,&header.maxDAC ,&Index );
			arm_min_q15 ( (q15_t)(dac) ,header.N/2+1 ,&header.minDAC ,&Index );
			arm_rms_q15 ( (q15_t)(dac) ,header.N/2+1 ,&header.rmsDAC );

			// trigger(2);

			header.id++;
			uartWriteByteArray ( UART_USB ,(uint8_t*)&header ,sizeof(struct header_struct ));

				 adcRead(CH1); //why?? hay algun efecto minimo en el 1er sample.. puede ser por el blinkeo de los leds o algo que me corre 10 puntos el primer sample. Con esto se resuelve.. habria que investigar el problema en detalle
		  }
		  gpioToggle ( LED1 );											 // este led blinkea a fs/2
		  while(cyclesCounterRead()< EDU_CIAA_NXP_CLOCK_SPEED/header.fs) // el clk de la CIAA es 204000000
			 ;
   }
}
