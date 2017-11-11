import csv
import io
import codecs
class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
      #  self.queue = cStringIO.StringIO()
        self.queue = io.BytesIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def main():
  print("Testing to write unicode in python csv")
  s="गुजरात "
  with open('/tmp/u1.csv', 'w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file, delimiter=',')
    writer.writerow(s.encode("UTF-8"))
# values = ( ["Ñ", "utf-8"])
# f = open('/tmp/eggs.csv', 'w', encoding="utf-8")
# writer = UnicodeWriter(f)
# writer.writerow(values)
if __name__ == '__main__':
  main()
