# Statistical Forgery Localization

Attempted implementation of the statistical approach towards aligned double-JPEG compression detection (ADJPEG) as laid out in the [paper](https://ieeexplore.ieee.org/document/6151134) by Bianchi and Piva.

The implementation uses a mixture model to estimate the first compression. The mixture $\alpha$ still has to be supplied manually, though it should get implemented in future versions.

## Usage

- pip install `requirements.txt`

```
usage: adjpeg [-h] [--dct-range range] [--quiet] [--debug] [--output OUTPUT] image_path

positional arguments:
  image_path            input image file path in JPEG format

options:
  -h, --help            show this help message and exit
  --dct-range range, -r range
                        integer range of zero-indexed DCT coefficients between 0 and 63 to be analysed. write as two integers with '-' in between. in 'a-b' the first coefficient is 'a' and the last coefficient
                        is 'b-1' (like the python range() method)
  --quiet, -q           non verbose program output.
  --debug, -d           very verbose program output.
  --output OUTPUT, -o OUTPUT
                        path to output file
```

## Algorithm

The algorithm is adapted from the [paper](https://ieeexplore.ieee.org/document/6151134) by Bianchi and Piva 2012.

## Probability distribution for single quantized DC coefficients (pNDQ)

pNDQ describes the probability distribution of a quantized DCT value $x$ to be part of the original distribution $p_0$, when quantized with quantization step $Q_2$.

```math
p(x | \mathcal{H}_0) = p_\text{NDQ}(x;Q_2)=\sum^{Q_2x+Q_2/2}_{v=Q_2x-Q_2/2}p_o(v)
```

This is already in the simplified model. However, we do not have access to $p_0$ in a real-world environment. In a previous [paper](https://ieeexplore.ieee.org/document/5946978) this approximation is done by recompression a cropped version of the tampered image with $Q_2$ to get $\tilde{h}(x)$.

```math
p(x|\mathcal{H}_0)=\tilde{h}(x)
```

## Probability distribution for double-quantized DC coefficients (pDQ)

pDQ describes an approximated probability distribution for quantized DTC value $x$ with quantization steps $Q_1$ and $Q_2$.

```math
(x | \mathcal{H}_1) = p_\text{DQ}(x;Q_1,Q_2) \approx n_\text{DQ}(x) \cdot p_\text{NDQ}(x;Q_2), x \neq 0
```

This approximation is the product of the image not being doubly compressed and a periodic function

```math
n_\text{DQ}(x) = (R(x)-L(x))/Q_2 > 0
```

```math
L(x) = Q_1(\lceil \frac{Q_2}{Q_1} (x-\frac{\mu_e}{Q_2}-\dfrac{1}{2}) \rceil - \dfrac{1}{2})
```

```math
R(x) = Q_1(\lfloor \frac{Q_2}{Q_1} (x-\frac{\mu_e}{Q_2}+\dfrac{1}{2}) \rfloor + \dfrac{1}{2})
```

The r/t error using the actual fft and ifft is not feasible as the entire 8x8 block has to be converted, with each quantization step having a latent effect on the rounding and truncating of the single values.

## ADJPEG localization

We do not approximate $\mu_e$ and $\sigma^2_e$ for our approach, as we only take AC coefficients into account for our analysis. DC coefficients can be selected manually, but they are disabled during default usage.

We estimate the distribution of the unquantized DCT coefficients using the following formula:

```math
p_v(h) = \frac{h(v)+1}{N+N_{\text{bin}}}
```

where N is the number of DCT coefficients (number of blocks in the image) and $N_{\text{bin}}$ is the number of bins in the histogram. h(v) is calculated by compressing a shifted version of the tampered image with QF 100.

The overall result is a likelihood map, which shows, which regions of an image are doubly compressed (does not go by SCF hypothesis).

The 2D arrays for $p(x | \mathcal{H}_0)$ and $p(x | \mathcal{H}_1)$ for every block in the image is calculated for each coefficient and the likelihood map is calculated as follows:

```math
\mathcal{L}(i,j) = \mathcal{L}(i,j)\cdot \frac{p(x(i,j) | \mathcal{H}_1; Q_1)}{p(x | \mathcal{H}_0)}
```
