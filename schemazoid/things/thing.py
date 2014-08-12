from schemazoid import micromodels as m


class Thing(m.Model):
    name = m.CharField()
    description = m.CharField()
    url = m.CharField()  # TODO Make URLField
    image = m.CharField()  # TODO Make URLField
