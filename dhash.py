import cv2

def calc_dhash(path):
    
    # Carica l'immagine da disco
    image = cv2.imread(path)

    #Converti l'immagine in scala di grigi 
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    #Riduci le dimensioni dell'immagine a 9x8 pixel
    resized_image = cv2.resize(gray_image, (9, 8))

    #Calcola la differenza di luminosità tra pixel    
    diff_pixel = (resized_image[:, 1:] > resized_image[:, :-1]).astype(int)
    
    #passaggio da matrice a stringa binaria
    binary_string = ''.join(str(bit) for bit in diff_pixel.flatten())

    # trasforma la stringa binaria in un numero esadecimale
    hash_hex = hex(int(binary_string, 2))

    return hash_hex[2:] 


#print(calc_dhash('file_progetto/lola.jpg'))