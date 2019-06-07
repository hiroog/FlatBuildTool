// FlatBuildTool 2019 Hiroyuki Ogasawara
// vim:ts=4 sw=4 noet:

#define Py_LIMITED_API 1
#include	<Python.h>

#define	WIN32_LEAN_AND_MEAN
#include	<windows.h>

#define	USE_DEBUG_PRINT		0
#define	USE_PYZFILE			0

#define	VersionStr1( ma, mi )	#ma ## #mi
#define	VersionStr0( ma, mi )	VersionStr1( ma, mi )
#define	VERSION_STR		VersionStr0( PY_MAJOR_VERSION, PY_MINOR_VERSION )


#ifdef WINDOWS
int WINAPI wWinMain(
	HINSTANCE hInstance,	  /* handle to current instance */
	HINSTANCE hPrevInstance,  /* handle to previous instance */
	LPWSTR lpCmdLine,		  /* pointer to command line */
	int nCmdShow			  /* show state of window */
)
#else
int wmain()
#endif
{
	const size_t	NAME_LENGTH= 32;
	size_t	length= wcslen( __wargv[0] ) + NAME_LENGTH;
	wchar_t	*filename= _alloca( (length + 2) * 2 * sizeof(wchar_t) );

	wchar_t **myargv = _alloca((__argc + 1) * sizeof(wchar_t*));
	myargv[0] = __wargv[0];
	memcpy(myargv + 1, __wargv, __argc * sizeof(wchar_t *));

	{
		wchar_t	*eptr= filename;
#if USE_DEBUG_PRINT
		printf( "arg=%d, len= %zd\n", __argc, length );
		printf( "ver=%s\n", VERSION_STR );
#endif

		wcscpy_s( filename, length + 1, __wargv[0] );
		{
			wchar_t	*ptr= filename;
			for(; *ptr ; ptr++ ){
				if( *ptr == L'/' || *ptr == L'\\' ){
					eptr= ptr + 1;
				}
			}
			wcscpy_s( eptr, NAME_LENGTH, L"python" VERSION_STR ".zip;." );
			if( eptr != filename ){
				eptr[-1]= L'\0';
				wcscpy_s( eptr + 13, length, filename );
				eptr[-1]= '/';
			}
		}
#if USE_DEBUG_PRINT
		printf( "setpath=%ls\n", filename );
#endif
		Py_SetPath( filename );

#if USE_PYZFILE
		wcscpy_s( eptr, NAME_LENGTH, L"flmake.pyz" );
#endif
	}

#if USE_PYZFILE
	myargv[1]= filename;
#endif
#if USE_DEBUG_PRINT
	for( int i= 0 ; i< __argc+1 ; i++ ){
		printf( "arg[%d]=%ls\n", i, myargv[i] );
	}
#endif

	return Py_Main(__argc+1, myargv);
}
