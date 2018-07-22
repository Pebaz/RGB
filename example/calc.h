#ifndef CALC_H
#define CALC_H

/*
Adds two numbers together and returns the result.
*/
__declspec(dllexport) float __cdecl colonist_add(float x, float y);

/*
Subtracts two numbers together and returns the result.
*/
__declspec(dllexport) float __cdecl colonist_sub(float x, float y);

/*
Multiplies two numbers together and returns the result.
*/
__declspec(dllexport) float __cdecl colonist_mul(float x, float y);

/*
Divides two numbers together and returns the result.
*/
__declspec(dllexport) float __cdecl colonist_div(float x, float y);

#endif // CALC_H