import os
import cv2
import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import ImageGrid

from puzzle_data import puzzles

highlighted_fig = None


def print_image_rows(image):
    for row_idx in range(len(image)):
        image_row = image[row_idx]
        image_row_str = ''
        for pixel_rgb_idx in range(len(image_row)):
            image_row_str += '[ ' + str(image_row[0]) + ' ' + str(image_row[1]) + ' ' + str(image_row[2]) + ' ] '
        print(str(row_idx) + ' : ' + image_row_str)
        print('-----------------------------------------')


def print_tmp_parameters(piece_height, piece_width, k_h, potential_height, k_w, potential_width, k_ratio):
    print('single piece height : ' + str(piece_height))
    print('single piece width : ' + str(piece_width))
    print('k_h: ' + str(k_h) + ' , potential_height: ' + str(potential_height))
    print('k_w: ' + str(k_w) + ' , potential_width: ' + str(potential_width))
    print('k_w / k_h : ' + str(k_ratio))
    print('-' * 10)


def two_pieces_mse(image_a, image_b):
    # the 'Mean Squared Error' between the two images is the
    # sum of the squared difference between the two images;
    # NOTE: the two images must have the same dimension
    err = np.square(np.subtract(image_a, image_b)).mean()

    # return the MSE, the lower the error, the more "similar"
    # the two images are
    return err


def is_pair_in_subset(pair, subset):
    for subset_pair in subset:
        a = subset_pair[0]
        b = subset_pair[1]
        if a == pair[0] and b == pair[1]:
            return True
    return False


def pair_lists_difference(basic_list, subset):
    difference_list = []
    for pair in basic_list:
        if not is_pair_in_subset(pair, subset):
            difference_list.append(pair)
    return difference_list


def find_unique_values(subset):
    unique_values = []
    for pair in subset:
        a, b = pair
        if a not in unique_values:
            unique_values.append(a)
        if b not in unique_values:
            unique_values.append(b)
    return unique_values


def generate_border_image(image_to_add_border, border_thickness, color_name):
    img_height = image_to_add_border.shape[0]
    img_width = image_to_add_border.shape[1]
    cut_width = img_width - 2 * border_thickness
    cut_height = img_height - 2 * border_thickness

    cut_image = cv2.resize(image_to_add_border, (cut_width, cut_height))

    if color_name == 'orange':
        color = [252, 105, 0]
    elif color_name == 'blue':
        color = [0, 0, 255]
    else:
        color = [0, 0, 0]

    out_img = cv2.copyMakeBorder(
        cut_image,
        border_thickness,
        border_thickness,
        border_thickness,
        border_thickness,
        cv2.BORDER_CONSTANT,
        value=color
    )

    out_img_shape = out_img.shape

    return out_img


def find_second_pair_index(subset, position_to_place_piece):
    for index in range(0, len(subset)):
        pair = subset[index]
        if pair[0] == position_to_place_piece:
            return index

    return -1


class Puzzle:

    def show_whole_picture(self):
        plt.imshow(self.picture_image)

    #################################### FAZA INCJALIZACJI #########################################

    # załaduj zdjęcie puzzli i mozaikę do ułożenia
    def load_puzzle_data(self):
        self.load_picture()
        self.initialize_picture_data()
        self.load_mosaic()
        self.initialize_mosaic_data()

    #załaduj obrazek
    def load_picture(self):
        # ścieżka do pliku z obrazkiem
        picture_path = self.puzzle_picture_path(self.puzzle_num)
        # załaduj obrazek, biblioteka cv2
        self.picture_image = cv2.imread(picture_path, cv2.IMREAD_COLOR)
        # przekonwertuj do RGB
        self.picture_image = cv2.cvtColor(self.picture_image, cv2.COLOR_BGR2RGB)

    @staticmethod
    def puzzle_picture_path(puzzle_num):
        folder = './puzzles/'
        puzzle_folder = str(puzzle_num) + '/'

        filepath = os.path.join(folder, puzzle_folder, str(puzzle_num) + '.png')
        return filepath

    def initialize_picture_data(self):
        # ustaw początkową wysokość obrazka
        self.picture_initial_height = len(self.picture_image)
        # ustaw początkową szerokość obrazka
        self.picture_initial_width = len(self.picture_image[0])
        # common(for picture and mosaic) target range for piece height, basing on picture
        self.max_piece_height = math.floor(self.picture_initial_height / self.pieces_in_col)# + 1
        self.min_piece_height = math.floor(self.max_piece_height / 4)

    def load_mosaic(self):
        mosaic_path = self.puzzle_mosaic_path(self.puzzle_num)
        # ustaw początkową wysokość mozaiki
        self.mosaic_image = cv2.imread(mosaic_path)
        # ustaw początkową szerokość mozaiki
        self.mosaic_image = cv2.cvtColor(self.mosaic_image, cv2.COLOR_BGR2RGB)

    def initialize_mosaic_data(self):
        self.mosaic_initial_height = len(self.mosaic_image)
        self.mosaic_initial_width = len(self.mosaic_image[0])

    @staticmethod
    def puzzle_mosaic_path(puzzle_num):
        puzzle_folder = str(puzzle_num)
        filepath = os.path.join('.\puzzles', puzzle_folder, str(puzzle_num) + '_mosaic.png')
        return filepath

    #################################### FAZA INCJALIZACJI #########################################

    ###################### WYPISANIE POCZĄTKOWYCH I DOCELOWYCH ROZMIARÓW ###########################
    def print_picture_initial_dimensions(self):
        print(('-' * 10) + 'PICTURE-INITIAL-DIMENSIONS' + ('-' * 10))
        print('picture_initial_height : ' + str(self.picture_initial_height))
        print('picture_initial_width : ' + str(self.picture_initial_width))
        print(('-' * 10) + 'PICTURE-INITIAL-DIMENSIONS' + ('-' * 10))

    def print_picture_scaled_dimensions(self):
        print(('-' * 10) + 'PICTURE-TARGET--DIMENSIONS' + ('-' * 10))
        print('picture_scaled_height : ' + str(self.picture_target_height))
        print('picture_scaled_width : ' + str(self.picture_target_width))
        print(('-' * 10) + 'PICTURE-TARGET--DIMENSIONS' + ('-' * 10))

    ###################### WYPISANIE POCZĄTKOWYCH I DOCELOWYCH ROZMIARÓW ###########################

    def set_picture_scaled_dimensions(self, print_tmp_params):
        # rozważenie wszystkich możliwych (na ustalonych zasadach) wielkości pojedynczego puzzla
        for piece_height in range(self.min_piece_height, self.max_piece_height):
            # potencjalna wspólna wysokość zdjęcia i mozaiki
            potential_height = self.pieces_in_col * piece_height

            # skala zmiany wysokości
            k_h = self.picture_initial_height / potential_height

            # szerokość po przeskalowaniu skalą k_h (zaokrąglenie do części całkowitej w dół)
            potential_width = math.floor(self.picture_initial_width / k_h)
            potential_width = potential_width - potential_width % self.pieces_in_row

            if potential_width % self.pieces_in_row == 0:
                piece_width = int(potential_width / self.pieces_in_row)
                k_w = self.picture_initial_width / potential_width
                k_ratio = k_w / k_h
                # szukanie największych rozmiarów dla stosunku k_ratio spełniającego dokładność do 0.01
                if 1 - k_ratio < 0.01:
                    self.picture_target_height = potential_height
                    self.picture_target_width = potential_width
                    if print_tmp_params:
                        print_tmp_parameters(piece_height, piece_width, k_h, potential_height, k_w, potential_width,
                                             k_ratio)

    #zainicjuj/wygeneruj przeskalowane obrazy oryginalnego zdjęcia i mozaiki
    def generate_scaled_images(self):
        self.scaled_picture_image = cv2.resize(self.picture_image,
                                               (self.picture_target_width, self.picture_target_height))
        self.scaled_mosaic_image = cv2.resize(self.mosaic_image,
                                              (self.picture_target_width, self.picture_target_height))

    def print_scaled_images(self):
        vertical_concatenation = np.concatenate((self.scaled_picture_image, self.scaled_mosaic_image), axis=0)

    def generate_picture_pieces_list(self):
        piece_height = int(self.picture_target_height / self.pieces_in_col)
        piece_width = int(self.picture_target_width / self.pieces_in_row)
        for y in range(0, self.scaled_picture_image.shape[0], piece_height):
            for x in range(0, self.scaled_picture_image.shape[1], piece_width):
                vertical_start = y
                vertical_end = y + piece_height
                horizontal_start = x
                horizontal_end = x + piece_width

                next_piece = self.scaled_picture_image[vertical_start:vertical_end, horizontal_start:horizontal_end, :]
                self.picture_tiles.append(next_piece)

    def show_picture_pieces_list(self):
        fig = plt.figure(figsize=(20., 20.))
        grid = ImageGrid(fig, 111,
                         nrows_ncols=(self.pieces_in_col, self.pieces_in_row),  # creates 2x2 grid of axes
                         axes_pad=0.1,  # pad between axes
                         )

        for ax, im in zip(grid, self.picture_tiles):
            ax.imshow(im)

        plt.show()

    def generate_mosaic_pieces_list(self):
        piece_height = int(self.picture_target_height / self.pieces_in_col)
        piece_width = int(self.picture_target_width / self.pieces_in_row)
        for i in range(0, self.scaled_mosaic_image.shape[0], piece_height):
            for j in range(0, self.scaled_mosaic_image.shape[1], piece_width):
                next_piece = self.scaled_mosaic_image[i:i + piece_height, j:j + piece_width, :]
                self.mosaic_tiles.append(next_piece)

    def show_mosaic_pieces_list(self):
        fig = plt.figure(figsize=(20., 20.))
        grid = ImageGrid(fig, 111,
                         nrows_ncols=(self.pieces_in_col, self.pieces_in_row),  # creates 2x2 grid of axes
                         axes_pad=0.1,  # pad between axes
                         )

        for ax, im in zip(grid, self.mosaic_tiles):
            ax.imshow(im)

        plt.show()

    def print_mosaic_initial_dimensions(self):
        print(('-' * 10) + 'MOSAIC-INITIAL-DIMENSIONS' + ('-' * 10))
        print('mosaic_initial_height : ' + str(self.mosaic_initial_height))
        print('mosaic_initial_width : ' + str(self.mosaic_initial_width))
        print(('-' * 10) + 'MOSAIC-INITIAL-DIMENSIONS' + ('-' * 10))

    def generate_match_list(self):
        for i in range(0, len(self.mosaic_tiles)):
            piece_match_index = 0
            piece_mse = two_pieces_mse(self.mosaic_tiles[i], self.picture_tiles[0])
            for piece_candidate_index in range(1, len(self.mosaic_tiles)):
                tmp_mse = two_pieces_mse(self.mosaic_tiles[i], self.picture_tiles[piece_candidate_index])
                if tmp_mse < piece_mse:
                    piece_match_index = piece_candidate_index
                    piece_mse = tmp_mse
            self.match_list.append([i, piece_match_index])

    def remove_correct_placed_mosaic_pieces(self, print_difference):
        for el in self.match_list:
            if el[0] != el[1]:
                self.match_list_not_correct.append(el)
        if print_difference:
            print('all pieces: ' + str(len(self.match_list)))
            print('all pieces matches not correct: ' + str(len(self.match_list_not_correct)))

    def print_pairs(self):
        for pair_ind in range(0, len(self.match_list_not_correct), 3):
            first = self.match_list_not_correct[pair_ind]
            second = self.match_list_not_correct[pair_ind + 1]
            third = self.match_list_not_correct[pair_ind + 2]
            print(str(first) + ' ' + str(second) + ' ' + str(third))

    def generate_covering_subsets(self):
        #print(self.match_list_not_correct)
        for pair_index in range(0, len(self.match_list_not_correct)):
            current_start_pair = self.match_list_not_correct[pair_index]

            # initial values
            subset = [current_start_pair]
            index_i = 0

            while True:
                pairs_to_choose = pair_lists_difference(self.match_list_not_correct, subset)
                new_pair_added = False

                # tymczasowy podzbiór do dodawania nowych par i "nienamieszania"
                subset_tmp = subset[:]

                for subset_pair_ind in range(index_i, len(subset)):
                    subset_pair_1st = subset[subset_pair_ind][0]
                    subset_pair_2nd = subset[subset_pair_ind][1]
                    for pair_to_choose_ind in range(0, len(pairs_to_choose)):
                        possible_pair_to_choose = pairs_to_choose[pair_to_choose_ind]
                        pair_to_choose_1st = possible_pair_to_choose[0]
                        pair_to_choose_2nd = possible_pair_to_choose[1]
                        if subset_pair_1st == pair_to_choose_2nd or subset_pair_2nd == pair_to_choose_1st:
                            if not is_pair_in_subset(possible_pair_to_choose, subset_tmp):
                                subset_tmp.append(possible_pair_to_choose)
                                if not new_pair_added:
                                    new_pair_added = True
                                    index_i = len(subset)

                subset = subset_tmp[:]

                # jeśli nie dodano nowej pary do podzbioru
                if not new_pair_added:
                    # jeśli nie dodano jeszcze takiego zbioru
                    if not self.subset_in_subsets(subset):
                        self.subsets.append(subset)
                    break

    def subset_in_subsets(self, new_subset):
        # find subset with same pairs as new_subset
        # subset, f.e. [ [1,2], [2,3], [3,1] ]
        for subset in self.subsets:
            for pair in subset:
                # we consider that at least one same pair is required to state that new potential subset is already in list
                if is_pair_in_subset(pair, new_subset):
                    return True

        return False

    def minimum_moves_to_solve(self):
        return len(self.match_list_not_correct) - len(self.subsets)

    def move_figure(self, f, x, y):
        """Move figure's upper left corner to pixel (x, y)"""
        backend = matplotlib.get_backend()
        if backend == 'TkAgg':
            f.canvas.manager.window.wm_geometry("+%d+%d" % (x, y))
        elif backend == 'WXAgg':
            f.canvas.manager.window.SetPosition((x, y))
        else:
            # This works for QT and GTK
            # You can also use window.setGeometry
            f.canvas.manager.window.move(x, y)

    def show_steps_for_subsets(self):
        for subset in self.subsets:
            self.show_steps_for_subset(subset)

    def show_steps_for_subset(self, subset):
        while len(subset) > 1:
            # generuje zbiór unikalnych puzzli w podzbiorze
            unique_tiles_indexes_in_subset = find_unique_values(subset)
            # self.generate_mosaic_highlighted_subset(unique_tiles_indexes_in_subset, False, [-1, -1] , 2)

            first_pair = subset[0]
            piece_to_move_position = first_pair[0]
            position_to_place_piece = first_pair[1]

            self.generate_mosaic_highlighted_subset(unique_tiles_indexes_in_subset, True, first_pair, 2)

            piece_to_move = self.mosaic_tiles[piece_to_move_position]
            piece_from_target_pos = self.mosaic_tiles[position_to_place_piece]
            self.mosaic_tiles[piece_to_move_position] = piece_from_target_pos
            self.mosaic_tiles[position_to_place_piece] = piece_to_move

            second_pair_index = find_second_pair_index(subset, position_to_place_piece)
            second_pair = subset[second_pair_index]

            subset[0] = [piece_to_move_position, second_pair[1]]
            subset.pop(second_pair_index)

    def generate_mosaic_highlighted_subset(self, unique_tiles, highlight_moved_pair=False, moved_pair=[-1, -1],
                                           border_thickness=2):
        mosaic_highlighted_subset = self.mosaic_tiles[:]

        print(moved_pair)
        ind1 = moved_pair[0]
        piece1_row = int(math.floor(ind1 / self.pieces_in_row))
        piece1_col = ind1 % self.pieces_in_row
        ind2 = moved_pair[1]
        piece2_row = int(math.floor(ind2 / self.pieces_in_row))
        piece2_col = ind2 % self.pieces_in_row

        for i in unique_tiles:
            if i != ind1 and i != ind2:
                mosaic_highlighted_subset[i] = generate_border_image(mosaic_highlighted_subset[i], border_thickness,
                                                                     'orange')

        if highlight_moved_pair:
            mosaic_highlighted_subset[ind1] = generate_border_image(mosaic_highlighted_subset[ind1], border_thickness,
                                                                    'blue')
            mosaic_highlighted_subset[ind2] = generate_border_image(mosaic_highlighted_subset[ind2], border_thickness,
                                                                    'blue')

        highlighted_fig = plt.figure(figsize=(7.7, 10))
        pair_title_part = "Pair: [" + str(ind1) + " , " + str(ind2) + "]"
        first_piece_coords_part = " - (1st piece: " + str(piece1_row) + " row " + str(piece1_col) + " col)"
        second_piece_coords_part = " - (2nd piece: " + str(piece2_row) + " row " + str(piece2_col) + " col)"
        fig_title = pair_title_part + first_piece_coords_part + second_piece_coords_part
        highlighted_fig.suptitle(fig_title)

        grid = ImageGrid(highlighted_fig, 111,
                         nrows_ncols=(self.pieces_in_col, self.pieces_in_row),  # creates 2x2 grid of axes
                         axes_pad=0.1,  # pad between axes
                         )

        tmp_ind = 0
        for ax, im in zip(grid, mosaic_highlighted_subset):
            ax.imshow(im)
            ax.set_title(str(tmp_ind))
            tmp_ind += 1

        self.move_figure(highlighted_fig, 760, 0)

        plt.show()

    def __init__(self, puzzle_obj):
        # numer puzzli
        self.puzzle_num = puzzle_obj["number"]
        # ilość puzzli w rzędzie
        self.pieces_in_row = puzzle_obj['pieces_in_row']
        # ilość puzzli w kolumnie
        self.pieces_in_col = puzzle_obj['pieces_in_col']

        # obraz puzzli
        self.picture_image = None
        # początkowa wysokość puzzli
        self.picture_initial_height = 0
        # początkowa szerokość puzzli
        self.picture_initial_width = 0
        self.min_piece_height = None
        self.max_piece_height = None

        # przeskalowane zdjęcie puzzli, transform(self.picture_image, scaleFactor), scaleFactor < 1
        self.scaled_picture_image = None
        # części zdjęcia, puzzle ułożone
        self.picture_tiles = []

        # docelowa wysokość zdjęcia
        self.picture_target_height = 0
        # docelowa szerokość zdjęcia
        self.picture_target_width = 0

        # mozaika (pomieszane puzzle)
        self.mosaic_image = None
        # początkowa wysokość mozaiki
        self.mosaic_initial_height = 0
        # początkowa szerokość mozaiki
        self.mosaic_initial_width = 0

        # przeskalowana mozaika
        self.scaled_mosaic_image = None
        # lista puzzli mozaiki
        self.mosaic_tiles = []

        self.match_list = []
        self.match_list_not_correct = []

        self.subsets = []


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    # load puzzle fro
    puzzle = Puzzle(puzzles.get("puzzle_337"))

    moves_to_beat = 75

    ################### INITIALIZE PART (START) ###################
    puzzle.load_puzzle_data()
    puzzle.set_picture_scaled_dimensions(False)
    puzzle.generate_scaled_images()
    #################### INITIALIZE PART (END) ####################
    puzzle.show_whole_picture()

    ######### DIVIDE PICTURE AND MOSAIC INTO PIECES(START) #########
    puzzle.generate_picture_pieces_list()
    puzzle.generate_mosaic_pieces_list()
    ########## DIVIDE PICTURE AND MOSAIC INTO PIECES(END) ##########

    puzzle.generate_match_list()

    puzzle.remove_correct_placed_mosaic_pieces(False)
    puzzle.generate_covering_subsets()

    minimum_moves = puzzle.minimum_moves_to_solve()
    print("minimum_moves count: " + str(minimum_moves))
    if minimum_moves < moves_to_beat:
        puzzle.show_steps_for_subsets()
