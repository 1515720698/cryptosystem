#pragma once

typedef struct
{
	unsigned long total[2];     /*!< number of bytes processed  */
	unsigned long state[8];     /*!< intermediate digest state  */
	unsigned char buffer[64];   /*!< data block being processed */

	unsigned char ipad[64];     /*!< HMAC: inner padding        */
	unsigned char opad[64];     /*!< HMAC: outer padding        */

}
sm3_context;

#ifdef __cplusplus
extern "C" {
#endif

	/**
	 * \brief          SM3 context setup
	 *
	 * \param ctx      context to be initialized
	 */
	void sm3_starts(sm3_context *ctx);

	/**
	 * \brief          SM3 process buffer
	 *
	 * \param ctx      SM3 context
	 * \param input    buffer holding the  data
	 * \param ilen     length of the input data
	 */
	void sm3_update(sm3_context *ctx, unsigned char *input, int ilen);

	/**
	 * \brief          SM3 final digest
	 *
	 * \param ctx      SM3 context
	 */
	void sm3_finish(sm3_context *ctx, unsigned char output[32]);

	/**
	 * \brief          Output = SM3( input buffer )
	 *
	 * \param input    buffer holding the  data
	 * \param ilen     length of the input data
	 * \param output   SM3 checksum result
	 */
	void sm3(unsigned char *input, int ilen,
		unsigned char output[32]);


	/**
	 * \brief          Output = SM3( file contents )
	 *
	 * \param path     input file name
	 * \param output   SM3 checksum result
	 *
	 * \return         0 if successful, 1 if fopen failed,
	 *                 or 2 if fread failed
	 */
	int sm3_file(char *path, unsigned char output[32]);
	 


#ifdef __cplusplus
}
#endif

 




