class Transform(object):
    def __init__(self, transform):
        self.x0 = 0
        self.y0 = 0
        self.kx, self.ky = transform["scale"]
        self.dx, self.dy = transform["translate"]

    def __call__(self, input, i):
        if not i:
            self.x0 = 0
            self.y0 = 0

        self.x0 += input[0]
        self.y0 += input[1]
        output = input.copy()
        output[0] = self.x0 * self.kx + self.dx
        output[1] = self.y0 * self.ky + self.dy

        return output

def identity(x):
    return x

def transform(transform):
    if transform is None:
        return identity
    return Transform(transform)
